# -*- encoding: utf-8 -*-
##############################################################################
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

import logging
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class StockPicking(orm.Model):

    _inherit = "stock.picking"

    _defaults = {
        'number_of_packages': 1,
    }


class StockPickingout(orm.Model):

    _inherit = "stock.picking.out"

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
    }


class StockMove(orm.Model):

    _inherit = "stock.move"

    def _update_average_price(self, cr, uid, move, context=None):
        super(StockMove, self)._update_average_price(
            cr, uid, move, context=context)

        product_obj = self.pool['product.product']
        uom_obj = self.pool['product.uom']
        product = move.product_id
        if (move.picking_id.type == 'out') and \
                (product.cost_method == 'average') and \
                (len(product.seller_ids) > 0):

            product_qty = move.product_qty
            product_uom = move.product_uom.id
            supplier = product.seller_ids[0]

            qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty,
                                       product.uom_id.id)
            if (product.qty_available - qty) <= 0:
                # Quantity will be 0 : put supplier price as standard price
                cr.execute('SELECT price '
                           'FROM pricelist_partnerinfo '
                           'WHERE suppinfo_id = %s'
                           'ORDER BY min_quantity DESC LIMIT 1',
                           (supplier.id,)
                res = cr.dictfetchone()
                if res:
                    product_obj.write(cr, uid, [product.id],
                                      {'standard_price': res['price']},
                                      context=context)
