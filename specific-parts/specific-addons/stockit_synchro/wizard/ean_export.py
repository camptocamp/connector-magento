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
import os
import netsvc

from osv import osv, fields
from tools.translate import _
from datetime import datetime
from tools import flatten
from stockit_synchro.stockit_exporter.exporter import StockitExporter


class StockItProductEANExport(osv.osv_memory):
    _name = 'stockit.export.product.ean13'
    _description = 'Export product EAN in Stock iT format'

    _columns = {
        'data': fields.binary('File', readonly=True),
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        rows = self.get_data(cr, uid, ids, context)
        exporter = StockitExporter()
        data = exporter.get_csv_data(rows)
        result = self.write(cr,
                            uid,
                            ids,
                            {'data': base64.encodestring(data)},
                            context=context)
        return result

    def create_request_error(self, cr, uid, err_msg, context=None):
        logger = netsvc.Logger()
        logger.notifyChannel(
                             _("Stockit Product EAN13 Export"),
                             netsvc.LOG_ERROR,
                             _("Error exporting product ean13 file : %s" % (err_msg,)))

        request = self.pool.get('res.request')
        summary = _("Stock-it product export EAN13 failed\n"
                    "With error:\n"
                    "%s") % (err_msg,)

        request.create(cr, uid,
                       {'name': _("Stock-it product EAN13 export"),
                        'act_from': uid,
                        'act_to': uid,
                        'body': summary,
                        })
        return True

    def run_background_export(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_base_path or not company.stockit_product_ean_export:
            raise osv.except_osv(_('Error'), _('Stockit path is not configured on company.'))
        now = datetime.now()
        filename = "product_ean_export_%i%i%i%i%i.csv" % (now.year, now.month, now.day, now.hour, now.minute)
        filepath = os.path.join(company.stockit_base_path,
                                company.stockit_product_ean_export,
                                filename)
        try:
            rows = self.get_data(cr, uid, [], context)
            exporter = StockitExporter(filepath)
            data = exporter.get_csv_data(rows)
            exporter.export_file(data)
        except Exception, e:
            self.create_request_error(cr, uid, str(e), context)
        return True

    def get_data(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        context = context or {}

        rows = []
        prod_ids = product_obj.search(cr, uid, [('type', '!=', 'service')],
                                      context=context)
        for product in product_obj.browse(cr, uid, prod_ids):
            ean13_list = [ean13.name for ean13 in product.ean13_ids]
            row = flatten([
                product.default_code,
                ean13_list
            ])
            rows.append(row)
        return rows

StockItProductEANExport()
