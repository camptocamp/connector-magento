# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2010-2012 Camptocamp SA
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

from osv import fields, osv


class Product(osv.osv):
    """ Inherit product in order to add the Negative Stock Magento's behavior
    and customized the message sent to Magento for update stocks
    """

    _inherit = 'product.product'

    _columns = {
        'magento_backorders': fields.selection(
            [('0', 'No Negative Stock Allowed'),
             ('1', 'Negative Stock Allowed'),
             ('2', 'Negative Stock Allowed (but warn customer)')],
             'Magento Backorder',
             help="A backorder the strategy to use for an item "
                  "that was in stock previously "
                  "but is temporarily out of stock. "
                  "Choose the Magento behavior here."),
        }

    _defaults = {
        'magento_backorders': lambda *a: '1',
        }

    def _prepare_inventory_magento_vals(self, cr, uid, product, stock, shop,
                                        context=None):
        """
        Prepare the values to send to Magento (message product_stock.update).
        Can be inherited to customize the values to send.

        Inherited in order to:
        use the field bom_stock for quantity
        add backorders and some fields to True

        Always put "is_in_stock" to True

        :param browse_record product: browseable product
        :param browse_record stock: browseable stock location
        :param browse_record shop: browseable shop
        :return: a dict of values to send to Magento with a call to :
        product_stock.update
        """
        # force the bom_stock field to be used to compute the qty
        vals = super(Product, self)._prepare_inventory_magento_vals(
            cr, uid, product, stock, shop, context=context)
        vals.update({
            'backorders': product.magento_backorders,
            'is_in_stock': True,
            'use_config_manage_stock': True,
            'manage_stock': True,
            'use_config_min_sale_qty': True,
            'use_config_max_sale_qty': True, })
        return vals

Product()
