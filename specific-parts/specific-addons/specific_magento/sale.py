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
from tools.translate import _


class sale_order(osv.osv):
    _inherit = "sale.order"

    def oe_create(self, cr, uid, vals, external_referential_id,
                  defaults=None, context=None):
        """call sale_markup's module on_change to compute margin
        when order's created from magento"""
        order_id = super(sale_order, self).oe_create(
            cr, uid, vals, external_referential_id,
            defaults=defaults, context=context)
        order_line_obj = self.pool.get('sale.order.line')
        order = self.browse(cr, uid, order_id, context)
        for line in order.order_line:
            # Call line oin_change to record margin
            line_changes = order_line_obj.onchange_price_unit(
                cr, uid, line.id, line.price_unit, line.product_id.id,
                line.discount, line.product_uom.id, order.pricelist_id.id)
            # Always keep the price from Magento
            line_changes['value']['price_unit'] = line.price_unit
            order_line_obj.write(
                cr, uid, line.id, line_changes['value'], context=context)

        return order_id

sale_order()


class sale_shop(osv.osv):

    _inherit = 'sale.shop'

    def deactivate_products(self, cr, uid, context=None):
        """
        Deactivate all products planned to deactivation on OpenERP
        Only if no picking uses the product
        """
        product_ids = self.pool.get('product.product').search(
            cr, uid, [('to_deactivate', '=', True)])
        self.pool.get('product.product').try_deactivate_product(
            cr, uid, product_ids, context=context)
        return True

    def export_catalog(self, cr, uid, ids, context=None):
        res = super(sale_shop, self).export_catalog(
            cr, uid, ids, context=context)
        self.deactivate_products(cr, uid, context=context)
        return res

sale_shop()
