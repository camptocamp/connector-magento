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

import base64
import datetime
from osv import osv, fields
from tools.translate import _
from operator import itemgetter
from itertools import groupby
from stockit_synchro.stockit_importer.importer import StockitImporter


class StockItInPickingImport(osv.osv_memory):
    _name = 'stockit.import.in.picking'
    _description = 'Import incoming pickings in Stock iT format'

    _columns = {
        'data': fields.binary('File', required=True),
        'filename': fields.char('Filename', size=256,
                                required=True, readonly=False),
    }

    def get_from_ftp(self, cr, uid, ids, context=None):
        """ Connect on the ftp and copy the file locally
        """
        pass

    def import_in_picking(self, cr, uid, ids, context=None):
        """ Import incoming pickings according to the Stock it file
        and returns the updated picking ids
        """
        if isinstance(ids, list):
            ids = ids[0]

        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        stock_move_obj = self.pool.get('stock.move')

        wizard = self.browse(cr, uid, ids, context)
        if not wizard.data:
            raise osv.except_osv(_('UserError'),
                                 _("You need to select a file!"))

        # header to apply on the csv file (no header on the file)
        # in the right order
        header = ['type', 'picking_name', 'planned_date', 'default_code',
                  'brand', 'expected_qty', 'received_qty', 'ean', 'width',
                  'length', 'height', 'picking_capacity', ]

        conversion_types = {
            'type': unicode,
            'picking_name': unicode,
            'planned_date': datetime.datetime,
            'default_code': unicode,
            'brand': unicode,
            'expected_qty': float,
            'received_qty': float,
            'ean': unicode,
            'width': float,
            'length': float,
            'height': float,
            'picking_capacity': float,
        }

        importer = StockitImporter()
        importer.read_from_base64(wizard.data)
        rows = importer.csv_to_dict(header)
        rows = importer.cast_rows(rows, conversion_types)

        # E means incoming product for stockit
        rows = [row for row in rows if row['type'] == 'E']

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
            product_obj.add_ean_if_not_exists(cr, uid,
                                              product_id,
                                              product_ean_list[product_id],
                                              context)

        # sum quantities of duplicate products in a packing and remove them
        rows = sorted(rows, key=itemgetter('picking_name', 'default_code'))
        if rows:
            last = rows[-1]
            for index in range(len(rows) - 2, -1, -1):
                if last['picking_name'] == rows[index]['picking_name'] and \
                   last['default_code'] == rows[index]['default_code']:
                    last['expected_qty'] = last['expected_qty'] + \
                                       rows[index]['expected_qty']
                    last['received_qty'] = last['received_qty'] + \
                                       rows[index]['received_qty']
                    del rows[index]
                else:
                    last = rows[index]

        imported_picking_ids = []

        for picking_name, rows in groupby(rows,
                                          lambda row: row['picking_name']):
            picking_ids = picking_obj.search(cr, uid,
                [('name', '=', picking_name)])
            if not picking_ids:
                raise Exception('ImportError', "Picking %s not found !" %
                                               (picking_name,))
            picking_id = picking_ids[0]
            imported_picking_ids.append(picking_id)
            picking = picking_obj.browse(cr, uid, picking_id)
            for row in rows:
                product_ids = product_obj.search(cr, uid,
                                                 [('default_code',
                                                   '=',
                                                   row['default_code'])])
                if not product_ids:
                    raise Exception('ImportError', "Product %s not found !" %
                                                   (row['default_code'],))
                product_id = product_ids[0]
                product = product_obj.browse(cr, uid, product_id)
                found_product = False
                for move in picking.move_lines:
                    if move.product_id.id == product_id:
                        found_product = True
                        if move.product_qty != row['received_qty']:
                            uos_qty = stock_move_obj.onchange_quantity(
                                        cr, uid, [],
                                        product_id,
                                        row['received_qty'],
                                        move.product_uom,
                                        move.product_uos,
                                        )['value']['product_uos_qty']
                            stock_move_obj.write(cr, uid, move.id,
                                                 {'product_qty': row['received_qty'],
                                                  'product_uos_qty': uos_qty,
                                                  })
                        break

                if not found_product:
                    # create a move line with the new product
                    loc_id = 7  # FIXME set right stock
                    loc_dest_id = 11  # FIXME set right stock
                    stock_move_values = stock_move_obj.onchange_product_id(
                        cr, uid, [],
                        prod_id=product_id,
                        loc_id=loc_id,
                        loc_dest_id=loc_dest_id,
                        address_id=picking.address_id.id
                    )['value']

                    stock_move_values.update({
                        'picking_id': picking_id,
                        'product_id': product_id,
                        'product_qty': row['received_qty'],
                    })

                    stock_move_values['product_uos_qty'] = \
                    stock_move_obj.onchange_quantity(
                        cr, uid, [],
                        product_id,
                        stock_move_values['product_qty'],
                        stock_move_values['product_uom'],
                        stock_move_values['product_uos'],
                        )['value']['product_uos_qty']

                    move_id = stock_move_obj.create(cr, uid, stock_move_values)
                    stock_move_obj.force_assign(cr, uid, move_id)  # FIXME is that right ? product IS available!

            #TODO confirm pickings ?

        return imported_picking_ids

    def action_import(self, cr, uid, ids, context=None):
        """ Update incoming pickings according the Stock it file
        """

        imported_picking_ids = self.import_in_picking(cr, uid, ids, context)
        res = {'type': 'ir.actions.act_window_close'}
        if imported_picking_ids:
            model_obj = self.pool.get('ir.model.data')
            model_data_ids = model_obj.search(cr, uid, [
                            ('model', '=', 'ir.ui.view'),
                            ('module', '=', 'stock'),
                            ('name', '=', 'view_picking_in_form')
                        ])
            resource_id = model_obj.read(cr, uid,
                                         model_data_ids,
                                         fields=['res_id'],
                                         context=context)[0]['res_id']

            res = {
                'name': _("Imported incoming pickings"),
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(False, 'tree'), (resource_id, 'form')],
                'domain': "[('id', 'in', %s)]" % imported_picking_ids,
                'context': context,
            }
        return res

StockItInPickingImport()
