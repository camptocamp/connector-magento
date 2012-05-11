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

from osv import fields, osv
from tools.translate import _


class Stock(osv.osv):
    """Inherit the stock.picking in order redefine the magento shipping"""

    _inherit = 'stock.picking'

    _columns = {
        # the next packing id (reverse of back order)
        'nextorder_id': fields.one2many(
            'stock.picking', 'backorder_id',
            string='Next Delivery Order',
            readonly=True),
        }

    def _create_custom_shipping(self, cr, uid, picking_id,
                                external_referential_id,
                                magento_incrementid, mail_notification=True, context=None):
        """Create a shipment in magento. The normal behavior of the
        magentoerpconnect methods has been overrided to handle the case
        of the modified products in a packing.
        For that purpose, we added a new parameter on the magento method
        sales_order_shipment.create which contains
        the product sku, old sku and quantity."""
        if context is None:
            context = {}
        conn = context['conn_obj']
        picking = self.pool.get('stock.picking').browse(
            cr, uid, picking_id, context=context)

        # used for magento custom parameter of
        # the method sales_order_shipment.create
        skus = []
        for line in picking.move_lines:
            old_sku = line.old_product_id and \
                      line.old_product_id.magento_sku or False

            # create a list with all product of the packing
            item = {
                    'sku': line.product_id.magento_sku,
                    'qty': line.product_qty,
                   }
            if old_sku:
                item.update({'old_sku': old_sku})
            skus.append(item)

        last_packing = False
        # if there is no other packing to do after this one,
        # we consider that this is the last
        if not len(picking.nextorder_id):
            last_packing = True

        ext_shipping_id = conn.call('sales_order_shipment.creer',
                                    [
                                    magento_incrementid,
                                    skus,
                                    _("Shipping Created"),
                                    mail_notification,
                                    True,
                                    last_packing
                                    ])

        return ext_shipping_id

    def create_ext_complete_shipping(self, cr, uid, id, external_referential_id, magento_incrementid, mail_notification=True, context=None):
        return self._create_custom_shipping(cr, uid, id, external_referential_id, magento_incrementid, mail_notification=True, context=context)

    def create_ext_partial_shipping(self, cr, uid, id, external_referential_id, magento_incrementid, mail_notification=True, context=None):
        return self._create_custom_shipping(cr, uid, id, external_referential_id, magento_incrementid, mail_notification=True, context=context)

Stock()
