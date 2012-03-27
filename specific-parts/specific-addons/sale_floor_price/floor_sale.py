# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
#    All Right Reserved
#
#    Author : Joel Grand-Guillaume (Camptocamp)
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from tools.translate import _

class SaleOrderLine(osv.osv):
    _inherit = 'sale.order.line'

    def _reach_floor_price(self, cr, uid, floor_price, discount, price_unit):
        sell_price = price_unit * (1 - (discount or 0.0) / 100.0)
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price')
        sell_price = round(sell_price, precision)
        if (sell_price < floor_price):
            return True
        return False

    def _compute_lowest_discount(self, cr, uid, floor_price, price_unit):
        diff = (floor_price - price_unit)
        disc = diff / price_unit
        return abs(round(disc*100,2))

    def _compute_lowest_price(self, cr, uid, floor_price, discount):
        if discount == 100.0:
            res = 0.0
        else:
            res = floor_price / (1-(discount / 100.0))
        return res

    def product_id_change(self,cr, uid, ids, *args, **kwargs):
        '''
        Overload method:
            - Empty the discount when changing.
        '''
        res = super(SaleOrderLine, self).product_id_change(cr, uid, ids, *args, **kwargs)

        res['value']['discount'] = 0.0
        return res


    def onchange_price_unit(self, cr, uid, ids, price_unit, product_id, discount, product_uom,
                            pricelist, override_unit_price = True):
        '''
        If price unit change, check that it is not < floor_price_limit of related product.
        If override_unit_price is True, we put in price_unit the min possible value, otherwise
        we leave it empty...
        '''
        res = super(SaleOrderLine, self).onchange_price_unit(cr, uid, ids, price_unit,
                                                             product_id, discount, product_uom,
                                                             pricelist, override_unit_price=override_unit_price)
        res['value'] = res.get('value', {})

        if product_id and price_unit > 0.0:
            product_obj = self.pool.get('product.product')
            prod = product_obj.browse(cr,uid,product_id)
            if self._reach_floor_price(cr, uid, prod.floor_price_limit, discount, price_unit):
                if override_unit_price:
                    res['value']['price_unit'] = self._compute_lowest_price(cr ,uid, prod.floor_price_limit, discount)
                else:
                    res['value']['price_unit'] = price_unit
                str_tuple = (price_unit, discount, prod.floor_price_limit, res['value']['price_unit'])
                warn_msg = _(("You selected a unit price of %d.- with %.2f discount."
                              "\nThe floor price has been set to %d"
                              ".-, so the mininum allowed value is %d.") % str_tuple)

                warning = {'title': _('Floor price reached !'),
                           'message': warn_msg}
                res['warning'] = warning
                res['domain'] = {}
        return res

    def onchange_discount(self, cr, uid, ids, price_unit, product_id, discount, product_uom, pricelist):
        '''
        If discount change, check that final price is not < floor_price_limit of related product
        '''
        res = super(SaleOrderLine, self).onchange_discount(cr, uid, ids, price_unit, product_id,
                                                           discount, product_uom, pricelist)
        
        res['value'] = res.get('value', {})

        if product_id and price_unit > 0.0:
            product_obj = self.pool.get('product.product')
            prod = product_obj.browse(cr,uid,product_id)
            if self._reach_floor_price(cr, uid, prod.floor_price_limit, discount, price_unit):
                res['value']['discount'] = self._compute_lowest_discount(cr,uid,prod.floor_price_limit,price_unit)
                str_tuple = (discount,price_unit,prod.floor_price_limit,res['value']['discount'])
                warn_msg = _(("You selected a discount of %.2f with a unit price of %d.-."
                             "\nThe floor price has been set to %d.-, so "
                             "the maximum discount allowed is %d.") % str_tuple)
                warning = {
                    'title': _('Floor price reached !'),
                    'message': warn_msg
                    }
                res['warning'] = warning
                res['domain'] = {}
        return res
