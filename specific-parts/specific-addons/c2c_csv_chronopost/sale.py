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
import netsvc
from osv import fields,osv

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def action_ship_create(self, cr, uid, ids, *args):
        """If a product CASH ON DELIVERY MAGENTO exists in the order, we add its amount in the cash on delivery field"""
        result = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.order_line:
                if line.product_id and line.product_id.default_code == 'CASH ON DELIVERY MAGENTO':
                    pids = [picking.id for picking in order.picking_ids]
                    self.pool.get('stock.picking').write(cr, uid, pids, {
                        'cash_on_delivery_amount_untaxed': order.amount_untaxed,
                        'cash_on_delivery_amount': order.amount_total,
                    })
                    break
        return result
    
sale_order()