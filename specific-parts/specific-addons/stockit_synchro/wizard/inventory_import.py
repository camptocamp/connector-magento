# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from osv import osv, fields
from tools.translate import _
from operator import itemgetter
from stockit_synchro.stockit_importer.importer import StockitImporter


class StockItInventoryImport(osv.osv_memory):
    _name = 'stockit.import.inventory'
    _description = 'Import inventories in Stock iT format'

    _columns = {
        'data': fields.binary('File', required=True),
        'filename': fields.char('Filename',
                                size=256,
                                required=True,
                                readonly=False),
    }

    def get_from_ftp(self, cr, uid, ids, context=None):
        """ Connect on the ftp and copy the file locally
        """
        pass

    def import_inventory(self, cr, uid, ids, context=None):
        """ Import inventories according to the Stock it file
        and returns the created inventory id
        """
        if isinstance(ids, list):
            ids = ids[0]

        inventory_id = False
        inventory_obj = self.pool.get('stock.inventory')
        product_obj = self.pool.get('product.product')

        wizard = self.browse(cr, uid, ids, context)
        if not wizard.data:
            raise osv.except_osv(_('UserError'),
                                 _("You need to select a file!"))

        header = ['type', 'default_code', 'quantity', 'ean', 'zone']
        conversion_types = {
            'type': unicode,
            'default_code': unicode,
            'quantity': int,
            'ean': unicode,
            'zone': unicode,
        }

        importer = StockitImporter()
        importer.read_from_base64(wizard.data)
        rows = importer.csv_to_dict(header)
        rows = importer.cast_rows(rows, conversion_types)

        # I means inventory for stock it
        rows = [row for row in rows if row['type'] == 'I']

        # create ean on product if it does not already exist
        product_ean_list = {}
        for row in rows:
            product_ids = product_obj.search(cr, uid,
                [('default_code', '=', row['default_code'])])
            product_id = product_ids[0]
            if product_id not in product_ean_list.keys():
                product_ean_list[product_id] = []
            product_ean_list[product_id].append(row['ean'])

        for product_id in product_ean_list:
            product_obj.add_ean_if_not_exists(cr, uid, product_id, product_ean_list[product_id], context)

        # sum quantities of duplicate products and remove them
        rows = sorted(rows, key=itemgetter('default_code', 'zone'))
        if rows:
            last = rows[-1]
            for index in range(len(rows) - 2, -1, -1):
                if last['default_code'] == rows[index]['default_code'] and \
                   last['zone'] == rows[index]['zone']:
                    last['quantity'] = last['quantity'] + \
                                       rows[index]['quantity']
                    del rows[index]
                else:
                    last = rows[index]

        inventory_rows = []
        for row in rows:
            product_ids = product_obj.search(cr, uid,
                [('default_code', '=', row['default_code'])])
            if not product_ids:
                raise Exception('ImportError', "Product code %s not found !" %
                                               (row['default_code'],))
            product_id = product_ids[0]
            product_uom = product_obj.browse(cr, uid, product_id).uom_id

            inventory_row = {'product_id': product_id,
                             'product_qty': row['quantity'],
                             'product_uom': product_uom.id,  # TODO use onchange
                             'location_id': 11,  # FIXME get the right location
                             #select in wizard or get info zone from the file?
                             }
            inventory_rows.append(inventory_row)

        if inventory_rows:
            inventory_id = inventory_obj.create(cr, uid,
                    {'name': _('Stockit inventory'),
                     'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                     'inventory_line_id': [(0, 0, row)
                                            for row
                                            in inventory_rows]}
            )
        return inventory_id

    def action_import(self, cr, uid, ids, context=None):
        """ Import inventories according to the Stock it file
        for frontend action, opens the form with the created inventory
        """
        inventory_id = self.import_inventory(cr, uid, ids, context)
        res = {'type': 'ir.actions.act_window_close'}
        if inventory_id:
            model_obj = self.pool.get('ir.model.data')
            model_data_ids = model_obj.search(cr, uid, [
                            ('model', '=', 'ir.ui.view'),
                            ('module', '=', 'stock'),
                            ('name', '=', 'view_inventory_form')
                        ])
            resource_id = model_obj.read(cr, uid, model_data_ids,
                                         fields=['res_id'],
                                         context=context)[0]['res_id']

            res = {
                'name': _("Imported inventory"),
                'type': 'ir.actions.act_window',
                'res_model': 'stock.inventory',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(False, 'tree'), (resource_id, 'form')],
                'domain': "[('id', '=', %s)]" % (inventory_id,),
                'context': context,
            }
        return res

StockItInventoryImport()
