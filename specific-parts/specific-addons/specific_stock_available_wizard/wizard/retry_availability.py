# -*- coding: utf-8 -*-
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

from osv import osv, fields


class StockPickingRetryAvailability(osv.osv_memory):
    _name = "stock.picking.retry.availability"
    _columns = {
    }

    def action_retry_assign(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')

        pick_obj.retry_assign_all(cr, uid, [], context=None)

        return {'type': 'ir.actions.act_window_close'}

StockPickingRetryAvailability()
