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
from osv import osv, fields
from tools.translate import _
from tools import flatten
from stockit_synchro.stockit_exporter.exporter import StockitExporter


class StockItProductEANExport(osv.osv_memory):
    _name = 'stockit.export.product.ean13'
    _description = 'Export product EAN in Stock iT format'

    _columns = {
        'filename': fields.char('Filename', 256, readonly=True),
    }

    def export(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')

        rows = []
        prod_ids = product_obj.search(cr, uid, [('type', '!=', 'service')], context=context)
        for product in product_obj.browse(cr, uid, prod_ids):
            ean13_list = [ean13.name for ean13 in product.ean13_ids]
            row = flatten([
                product.default_code,
                ean13_list
            ])
            rows.append(row)

        self.write_file(cr, uid, ids, rows, context)

    def write_file(self, cr, uid, ids, data, context=None):
        filename = '/tmp/product_ean13_export.csv'  # TODO: set a filename: manual / generated filename ?
        exporter = StockitExporter(filename)
        exporter.export_file(data)
        result = self.write(cr,
                            uid,
                            ids,
                            {'filename': filename, },
                            context=context)
        return result

StockItProductEANExport()
