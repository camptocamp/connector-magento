# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

import logging

from openerp.addons.connector.unit.mapper import ImportMapChild
from .backend import magento_debonix

_logger = logging.getLogger(__name__)


@magento_debonix
class LineMapChild(ImportMapChild):
    """ Customize the mapping of sales order lines.

    Delete sale order lines where the product is a component of a BoM
    and have a 0.0 price.

    We have to do that because Magento send the pack and his components
    in the sale order.

    And we don't want the components in the sales order, they are added
    in the delivery order with sale_bom_split.

    """
    _model_name = 'magento.sale.order.line'

    def format_items(self, items_values):
        items = items_values[:]
        for item in items_values:
            product_id = item['product_id']
            if product_id:
                # search if product is a BoM if it is, loop on other products
                # to search for his components to drop
                product = self.session.browse('product.product', product_id)

                if not product.bom_ids:
                    continue

                # search the products components of the BoM (always one
                # level when imported from magento)
                bom_prod_ids = set()
                for bom in product.bom_ids:
                    bom_prod_ids |= set(
                        [bom_line.product_id.id for bom_line in bom.bom_lines]
                    )

                for other_item in items[:]:
                    if other_item['product_id'] == product_id:
                        continue

                    # remove the lines of the bom only when the price is 0.0
                    # because we don't want to remove a component that
                    # is ordered alone
                    if other_item['product_id'] in bom_prod_ids and \
                       not other_item['price_unit']:
                        items.remove(other_item)

        return [(0, 0, item) for item in items]


# ---- BELOW: TO REVIEW ----
# from osv import osv
# from tools.translate import _


#TODO reimplement after implementation of the new markup module
#   in the project
#class sale_order(osv.osv):
#    _inherit = "sale.order"
#
#    def oe_create(self, cr, uid, vals, external_referential_id,
#                  defaults=None, context=None):
#        """call sale_markup's module on_change to compute margin
#        when order's created from magento"""
#        order_id = super(sale_order, self).oe_create(
#            cr, uid, vals, external_referential_id,
#            defaults=defaults, context=context)
#        order_line_obj = self.pool.get('sale.order.line')
#        order = self.browse(cr, uid, order_id, context)
#        for line in order.order_line:
#            # Call line oin_change to record margin
#            line_changes = order_line_obj.onchange_price_unit(
#                cr, uid, line.id, line.price_unit, line.product_id.id,
#                line.discount, line.product_uom.id, order.pricelist_id.id)
#            # Always keep the price from Magento
#            line_changes['value']['price_unit'] = line.price_unit
#            order_line_obj.write(
#                cr, uid, line.id, line_changes['value'], context=context)
#
#        return order_id
#
#sale_order()
