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
import tempfile
import os
from osv import osv, fields
from tools.translate import _
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

    def action_background_export(self, cr, uid, ids, context=None):
        # TODO: set a filename: manual / generated filename ?
        filename = os.path.join(tempfile.gettempdir(), 'product_export.csv')
        rows = self.get_data(cr, uid, ids, context)
        exporter = StockitExporter(filename)
        data = exporter.get_csv_data(rows)
        exporter.export_file(data)

    def get_data(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
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
