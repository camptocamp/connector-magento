# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import os
import glob
import netsvc
import pooler

from osv import osv, fields
from tools.translate import _
from operator import itemgetter
from stockit_synchro.stockit_importer.importer import StockitImporter
from wizard_utils import archive_file


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

    def import_inventory(self, cr, uid, ids, context=None):
        """ Import inventories according to the Stock it file
        and returns the created inventory id
        """
        if context is None:
            context = {}
        if isinstance(ids, list):
            ids = ids[0]

        logger = netsvc.Logger()
        inventory_id = False
        inventory_obj = self.pool.get('stock.inventory')
        product_obj = self.pool.get('product.product')

        wizard = self.browse(cr, uid, ids, context)
        if not wizard.data:
            raise osv.except_osv(_('UserError'),
                                 _("You need to select a file!"))

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        default_location_id = company.stockit_inventory_location_id

        header = ['type', 'default_code', 'quantity']
        conversion_types = {
            'type': unicode,
            'default_code': unicode,
            'quantity': int,
        }

        importer = StockitImporter()
        importer.read_from_base64(wizard.data)
        rows = importer.csv_to_dict(header)
        rows = importer.cast_rows(rows, conversion_types)

        # I means inventory for stock it
        rows = [row for row in rows if row['type'] == 'I']

        errors_report = []
        for row in rows:
            ctx = dict(context, active_test=False)
            product_ids = product_obj.search(
                cr, uid,
                [('default_code', '=', row['default_code'])],
                context=ctx)
            if not product_ids:
                errors_report.append(_('Product with default code %s does not exist!') % (row['default_code'],))
                continue
            product_id = product_ids[0]

        if errors_report:
            raise osv.except_osv(_('ImportError'), "\n".join(errors_report))

        # sum quantities of duplicate products and remove them
        rows = sorted(rows, key=itemgetter('default_code'))
        if rows:
            last = rows[-1]
            for index in range(len(rows) - 2, -1, -1):
                if last['default_code'] == rows[index]['default_code']:
                    last['quantity'] = last['quantity'] + \
                                       rows[index]['quantity']
                    del rows[index]
                else:
                    last = rows[index]

        inventory_rows = []
        for row in rows:
            try:
                ctx = dict(context, active_test=False)
                product_ids = product_obj.search(
                    cr, uid,
                    [('default_code', '=', row['default_code'])],
                    context=ctx
                )

                if not product_ids:
                    raise Exception('ImportError', "Product code %s not found !" %
                                                   (row['default_code'],))
                product_id = product_ids[0]
                product = product_obj.browse(cr, uid, product_id)
                if not product.active:
                    logger.notifyChannel(_("Stockit inventory import"),
                                         netsvc.LOG_WARNING,
                                         _("Product %s is deactivated. Skipped." % (product.default_code,)))
                    continue

                product_uom = product.uom_id

                inventory_row = {'product_id': product_id,
                                 'product_qty': row['quantity'],
                                 'product_uom': product_uom.id,
                                 'location_id': default_location_id.id,
                                 }
                inventory_rows.append(inventory_row)
            except osv.except_osv, e:
                errors_report.append(_('Processing error append: %s') % (e.value, ))
            except Exception, e:
                errors_report.append(_('Processing error append: %s') % (str(e)))
        if errors_report:
            raise osv.except_osv(_('ImportError'), "\n".join(errors_report))
        if inventory_rows:
            inventory_id = inventory_obj.create(cr, uid,
                    {'name': _('Stockit inventory'),
                     'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                     'inventory_line_id': [(0, 0, row)
                                            for row
                                            in inventory_rows]})
            inventory_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventory_obj.action_done(cr, uid, [inventory_id], context=context)

        return inventory_id

    def action_import(self, cr, uid, ids, context=None):
        """ Import inventories according to the Stock it file
        for frontend action, opens the form with the created inventory
        """
        #Wizard call from XML RPC transaction are atomic
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

    def create_request_error(self, cr, uid, file, err_msg, context=None):
        logger = netsvc.Logger()
        logger.notifyChannel(
                             _("Stockit inventory import"),
                             netsvc.LOG_ERROR,
                             _("Error importing inventory file %s : %s") % (file, err_msg))

        request = self.pool.get('res.request')
        summary = _("Stock-it inventory import failed on file : %s\n"
                    "With error:\n"
                    "%s") % (file, err_msg)

        request.create(cr, uid,
                       {'name': _("Stock-it inventory import"),
                        'act_from': uid,
                        'act_to': uid,
                        'body': summary,
                        })
        return True

    def run_background_import(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_base_path or not company.stockit_inventory_import:
            raise osv.except_osv(_('Error'), _('Stockit path is not configured on company.'))

        files_folder = os.path.join(company.stockit_base_path,
                                    company.stockit_inventory_import)
        files = glob.glob(os.path.join(files_folder, '*.*'))
        for file in files:
            inventory_id = False
            data_file = open(file, 'r')
            try:
                data = data_file.read().encode("base64")
                wizard = self.create(cr, uid, {'data': data}, context=context)
                try:
                    db, pool = pooler.get_db_and_pool(cr.dbname)
                    mycursor = db.cursor()
                    inventory_id = self.import_inventory(mycursor, uid, [wizard], context)
                    mycursor.commit()
                except Exception, e:
                    mycursor.rollback()
                    raise e
                finally:
                    mycursor.close()
            except osv.except_osv, e:
                self.create_request_error(cr, uid, file, e.value, context)
            except Exception, e:
                self.create_request_error(cr, uid, file, str(e), context)
            finally:
                data_file.close()
            if inventory_id:
                archive_file(file)
        return True

StockItInventoryImport()
