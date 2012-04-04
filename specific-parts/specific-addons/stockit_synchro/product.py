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

from osv import osv


class ProductProduct(osv.osv):

    _inherit = 'product.product'

    def add_ean_if_not_exists(self, cr, uid, product_id, ean_list, context=None):
        """ Given a list of EAN13, check on the product if it already exists
         and create it if not

         :param int product_id: id of the product
         :param list ean_list: list of ean13 as str to add on the product
         :return: True
        """
        product_ean_obj = self.pool.get('product.ean13')

        product = self.browse(cr, uid, product_id, context=context)

        existing_ean = [ean.name for ean in product.ean13_ids]
        ean_list = list(set(ean_list))  # remove duplicates
        for input_ean in ean_list:
            if not input_ean in existing_ean:
                product_ean_obj.create(
                    cr, uid,
                    {'name': input_ean,
                     'product_id': product_id},
                    context=context)
        return True

ProductProduct()
