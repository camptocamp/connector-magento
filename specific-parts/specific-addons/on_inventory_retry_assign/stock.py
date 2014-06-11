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
import logging

from openerp.osv import orm
_logger = logging.getLogger(__name__)


class stock_change_product_qty(orm.TransientModel):
    _inherit = "stock.change.product.qty"

    def change_product_qty(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        else:
            context = context.copy()
        context['from_product_stock_update'] = True
        return super(stock_change_product_qty, self).change_product_qty(
            cr, uid, ids, context=context)


class StockInventory(orm.Model):

    _inherit = "stock.inventory"

    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(StockInventory, self).action_done(
            cr, uid, ids, context=context)
        # the update stock button on the product creates an
        # inventory, we do not want it to trigger the 'assign all'
        if not context.get('from_product_stock_update'):
            self.pool.get('stock.picking').retry_assign_all(
                cr, uid, [], context=context)
        return res
