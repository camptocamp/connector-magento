# -*- coding: utf-8 -*-
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

from osv import osv, fields


class ProductProduct(osv.osv):
    _inherit = 'product.product'

    def add_ean_if_not_exists(self, cr, uid, id, ean_list, context=None):
        """ Given a list of EAN13, check on the product if it already exists
         and create it if not
        """
        product_ean_obj = self.pool.get('product.ean13')
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, id, context=context)
        ean_list = list(set(ean_list))  # remove duplicates
        for input_ean in ean_list:
            ean_exists = False
            max_sequence = 0
            for ean in product.ean13_ids:
                if ean.sequence > max_sequence:
                    max_sequence = ean.sequence
                if input_ean == ean.name:
                    ean_exists = True
            if not ean_exists:
                product_ean_obj.create(cr, uid,
                                       {'name': input_ean,
                                        'product_id': id,
                                        'sequence': max_sequence + 1,
                    })
        return True

ProductProduct()
