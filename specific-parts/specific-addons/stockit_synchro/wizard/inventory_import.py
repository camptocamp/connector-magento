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

import os
import glob
import logging
import time
import base64

from operator import itemgetter

from openerp import pooler
from openerp.osv import orm, fields
from openerp.tools.translate import _
from ..stockit_importer.importer import StockitImporter
from .wizard_utils import archive_file, create_claim


_logger = logging.getLogger(__name__)


class StockItInventoryImport(orm.TransientModel):
    _name = 'stockit.import.inventory'
    _description = 'Import inventories in Stock iT format'

    _columns = {
        'data': fields.binary('File', required=True),
        'filename': fields.char('Filename'),
    }

    def import_inventory(self, cr, uid, ids, context=None):
        """ Import inventories according to the Stock it file
        and returns the created inventory id
        """
        if context is None:
            context = {}
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "1 ID expected, got: %s" % ids
            ids = ids[0]

        inventory_id = False
        inventory_obj = self.pool.get('stock.inventory')
        product_obj = self.pool.get('product.product')
        attachment_obj = self.pool.get('ir.attachment')

        wizard = self.browse(cr, uid, ids, context)
        if not wizard.data:
            raise orm.except_orm(_('UserError'),
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
        # sum quantities of duplicate products and remove them
        rows = sorted(rows, key=itemgetter('default_code'))
        if rows:
            last = rows[-1]
            for index in range(len(rows) - 2, -1, -1):
                if last['default_code'] == rows[index]['default_code']:
                    last['quantity'] = (last['quantity'] +
                                        rows[index]['quantity'])
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
                    raise Exception("Product code %s not found !" %
                                    (row['default_code'],))
                product_id = product_ids[0]
                product = product_obj.browse(cr, uid, product_id)
                if not product.active:
                    _logger.info("Product %s is deactivated. Skipped.",
                                 product.default_code)
                    continue

                product_uom = product.uom_id

                inventory_row = {'product_id': product_id,
                                 'product_qty': row['quantity'],
                                 'product_uom': product_uom.id,
                                 'location_id': default_location_id.id,
                                 }
                inventory_rows.append(inventory_row)
            except orm.except_orm as e:
                errors_report.append(
                    _('Processing error append: %s') % (e.value,)
                )
            except Exception as e:
                errors_report.append(_('Processing error append: %s') % e)
        if inventory_rows:
            inventory_id = inventory_obj.create(
                cr, uid,
                {'name': _('Stockit inventory'),
                 'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                 'inventory_line_id': [(0, 0, row) for row in inventory_rows]}
            )
            # Use file name if available
            filename = wizard.filename or (
                "Stockit inventory file %s.csv" %
                (time.strftime('%Y-%m-%d %H:%M:%S'), )
            )
            attachment_data = {
                'name': filename,
                'datas': wizard.data,
                'datas_fname': filename,
                'res_model': 'stock.inventory',
                'res_id': inventory_id,
            }
            attachment_obj.create(cr, uid, attachment_data, context=context)
            try:
                inventory_obj.action_confirm(cr, uid,
                                             [inventory_id], context=context)
                inventory_obj.action_done(cr, uid,
                                          [inventory_id], context=context)
            except orm.except_orm as e:
                errors_report.append(_('Processing error append: %s') %
                                     (e.value,))
            except Exception as e:
                errors_report.append(_('Processing error append: %s') % e)

        return (inventory_id, errors_report)

    def action_import(self, cr, uid, ids, context=None):
        """ Import inventories according to the Stock it file
        for frontend action, opens the form with the created inventory
        """
        # Wizard call from XML RPC transaction are atomic
        (inventory_id, errors_report) = self.import_inventory(
            cr, uid, ids, context)
        if errors_report:
            raise orm.except_orm(
                _('Error:'),
                _("Stock-it inventory import failed "
                  "with error:\n"
                  "%s") % ("\n".join(errors_report),))
        res = {'type': 'ir.actions.act_window_close'}
        if inventory_id:
            model_obj = self.pool.get('ir.model.data')
            model_data_ids = model_obj.search(
                cr, uid,
                [('model', '=', 'ir.ui.view'),
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

    def post_error(self, cr, uid, filename, file_data, err_msg, context=None):
        _logger.exception("Error importing inventory file %s", filename)

        filename_no_path = os.path.split(filename)[1]

        title = _("Stock-it inventory %s") % (filename_no_path, )

        message = _("Stock-it inventory import failed on file: %s "
                    "with error:\n"
                    "%s") % (filename, err_msg)
        __, categ_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'stockit_synchro', 'categ_claim_stockit_inventory')

        create_claim(self, cr, uid, title, message, filename_no_path,
                     file_data, categ_id, context=context)
        return True

    def run_background_import(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if (not company.stockit_base_path or
                not company.stockit_inventory_import):
            raise orm.except_orm(
                _('Error'),
                _('Stockit path is not configured on company.'))

        files_folder = os.path.join(company.stockit_base_path,
                                    company.stockit_inventory_import)
        files = glob.glob(os.path.join(files_folder, '*.*'))
        for filename in files:
            inventory_id = False
            errors_report = []
            data_file = open(filename, 'r')
            try:
                data = data_file.read().encode("base64")
                db, pool = pooler.get_db_and_pool(cr.dbname)
                mycursor = db.cursor()
                try:
                    wizard = self.create(
                        mycursor, uid,
                        {'data': data,
                         'filename': os.path.split(filename)[1]},
                        context=context)
                    (inventory_id, errors_report) = self.import_inventory(
                        mycursor, uid, [wizard], context
                    )
                    mycursor.commit()
                except Exception as e:
                    mycursor.rollback()
                    raise
                finally:
                    mycursor.close()
            except orm.except_orm as e:
                errors_report.append(e.value)
            except Exception as e:
                errors_report.append(unicode(e))
            finally:
                if errors_report:
                    error_filename = archive_file(filename, in_error=True)
                    self.post_error(
                        cr, uid, error_filename, data,
                        "\n".join(errors_report), context)
                elif inventory_id:
                    archive_file(filename)
                data_file.close()
        return True
