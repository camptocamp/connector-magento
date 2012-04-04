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

import base64
import os
import netsvc

from osv import osv, fields
from tools.translate import _
from datetime import datetime
from stockit_synchro.stockit_exporter.exporter import StockitExporter


class StockItProductExport(osv.osv_memory):
    _name = 'stockit.export.product'
    _description = 'Export product in Stock iT format'

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
                             _("Stockit Product Export"),
                             netsvc.LOG_ERROR,
                             _("Error exporting product file : %s" % (err_msg,)))

        request = self.pool.get('res.request')
        summary = _("Stock-it product export failed\n"
                    "With error:\n"
                    "%s") % (err_msg,)

        request.create(cr, uid,
                       {'name': _("Stock-it product export"),
                        'act_from': uid,
                        'act_to': uid,
                        'body': summary,
                        })
        return True

    def run_background_export(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_base_path or not company.stockit_product_export:
            raise osv.except_osv(_('Error'), _('Stockit path is not configured on company.'))
        now = datetime.now()
        date_str = now.strftime('%Y%m%d%H%M%S')
        filename = "product_export_%s.csv" % (date_str,)
        filepath = os.path.join(company.stockit_base_path,
                                company.stockit_product_export,
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
        context['lang'] = 'fr_FR'

        rows = []
        prod_ids = product_obj.search(cr, uid, [('type', '!=', 'service')],
                                      context=context)
        for product in product_obj.browse(cr, uid, prod_ids):
            row = [
                product.default_code,
                product.name,
                '0',  # height
                '0',  # width
                '0',  # length
                product.weight_net and str(product.weight_net) or '0',
                product.weight and str(product.weight) or '0',
                product.categ_id.complete_name,  # Stock IT class A
                product.x_magerp_zdbx_default_marque and
                product.x_magerp_zdbx_default_marque.label or
                '',  # Stock IT class B
                '',  # Stock IT class C
                '0',
            ]
            rows.append(row)
        return rows

StockItProductExport()
