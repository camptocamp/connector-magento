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

    def oe_create(self, cr, uid, vals, data, external_referential_id,
                  defaults, context):
        """call sale_markup's module on_change to compute margin
        when order's created from magento"""
        order_id = super(sale_order, self).oe_create(
            cr, uid, vals, data, external_referential_id, defaults, context)
        order_line_obj = self.pool.get('sale.order.line')
        order = self.browse(cr, uid, order_id, context)
        for line in order.order_line:
            # Call line oin_change to record margin
            line_changes = order_line_obj.onchange_price_unit(
                cr, uid, line.id, line.price_unit, line.product_id.id,
                line.discount, line.product_uom.id, order.pricelist_id.id,
                line.property_ids, override_unit_price = False)
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

    def _create_magento_invoice(self, cr, uid, order, conn, ext_id, context=None):
        """ Creation of an invoice on Magento.
        Inherited to not write the invoice ref"""
        cr.execute("select account_invoice.id "
                   "from account_invoice "
                   "inner join sale_order_invoice_rel "
                   "on invoice_id = account_invoice.id "
                   "where order_id = %s" % order.id)
        resultset = cr.fetchone()
        created = False
        if resultset and len(resultset) == 1:
            invoice = self.pool.get("account.invoice").browse(
                cr, uid, resultset[0], context=context)
            if (invoice.amount_total == order.amount_total and
                not invoice.magento_ref):
                try:
                    conn.call(
                        'sales_order_invoice.create',
                        [order.magento_incrementid,
                         [],
                         _("Invoice Created"),
                         True,
                         order.shop_id.allow_magento_notification])
                    self.log(cr, uid, order.id,
                             "created Magento invoice for order %s" %
                             (order.id,))
                    created = True
                except Exception, e:
                    self.log(cr, uid, order.id,
                             "failed to create Magento invoice for order %s" %
                             (order.id,))
                    # TODO make sure that's because Magento invoice already
                    # exists and then re-attach it!
        return created

sale_shop()
