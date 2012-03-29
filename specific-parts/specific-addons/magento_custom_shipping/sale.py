# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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


class SaleOrder(osv.osv):

    _inherit = "sale.order"

    def create(self, cr, uid, vals, context=None):
        """ Before the creation of the sale order.
        Delete sale order lines with components of a BoM with a 0.0 price.
        We have to do that because Magento send the pack
        and his components in the sale order.
        We only delete the components with a 0.0 price
        because one may order a component independently.
        """
        product_obj = self.pool.get('product.product')

        if vals.get('order_line', False):
            # vals['order_line'] is: [(0, 0, {values})]
            for array_line in vals['order_line'][:]:
                line = array_line[2]
                product_id = line['product_id']

                if not product_id:
                    continue

                # search if product is a BoM if it is, loop on other products
                # to search for his components to drop
                product = product_obj.browse(cr, uid, product_id)

                if not product.bom_ids:
                    continue

                # compute the list of products components of the BoM
                bom_prod_ids = set()
                for bom in product.bom_ids:
                    bom_prod_ids |= set([bom_line.product_id.id
                                     for bom_line in bom.bom_lines])

                for other_array_line in vals['order_line'][:]:
                    other_line = other_array_line[2]
                    if other_line['product_id'] == product_id:
                        continue

                    # remove the lines of the bom where the price is 0.0
                    # because we don't want to remove it if it is ordered alone
                    if other_line['product_id'] in bom_prod_ids and \
                       not other_line['price_unit']:
                        vals['order_line'].remove(other_array_line)

        return super(SaleOrder, self).create(cr, uid, vals, context=context)

SaleOrder()
