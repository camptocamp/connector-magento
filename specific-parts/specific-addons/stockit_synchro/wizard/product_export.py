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
from stockit_synchro.file_writer.writer import UnicodeWriter


class StockItProductExport(osv.osv_memory):
    _name = 'product.export.stockit'
    _description = 'Export product in Stock-IT format'

    _columns = {
        'filename': fields.char('Filename', 256, readonly=True),
    }

    def get_brand_options(self, cr, uid, context):
        brand_dict = {}
        attributes_obj = self.pool.get('magerp.product_attributes')
        options_obj = self.pool.get('magerp.product_attribute_options')
        brand_attribute_id = attributes_obj.search(cr, uid, [('attribute_code', '=', 'zdbx_default_marque')], context=context)
        brand_option_ids = options_obj.search(cr, uid, [('attribute_id', '=', brand_attribute_id)], context=context)

        for option in options_obj.browse(cr, uid, brand_option_ids, context):
            brand_dict[option.id] = option.label
        return brand_dict

    def export(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')

        wiz = self.browse(cr, uid, ids)[0]

        brand_dict = self.get_brand_options(cr, uid, context)

        rows = []
        prod_ids = product_obj.search(cr, uid, [], context=context)
        for product in product_obj.browse(cr, uid, prod_ids):
            row = [
                product.default_code,
                product.name,
                '0',  # height
                '0',  # width
                '0',  # length
                product.weight_net and str(product.weight_net) or '',
                product.weight and str(product.weight) or '',
                '???',
                product.x_magerp_zdbx_default_marque and product.x_magerp_zdbx_default_marque.label or '',
                product.categ_id.complete_name,
                '???',
            ]
            rows.append(row)

        self.write_file(cr, uid, ids, rows, context)

    def write_file(self, cr, uid, ids, data, context=None):
        filename = '/tmp/product_export.csv'
        file = open(filename, 'w')
        writer = UnicodeWriter(file, delimiter='|')
        writer.writerows(data)
        file.close()
        result = self.write(cr,
                            uid,
                            ids,
                            {'filename': filename,},
                            context=context)
        return result

StockItProductExport()
