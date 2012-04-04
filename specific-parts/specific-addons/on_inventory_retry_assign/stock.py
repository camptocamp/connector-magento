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

from osv import osv


class StockPicking(osv.Model):

    _inherit = "stock.picking"

    def retry_assign_all(self, cr, uid, ids, context=None):
        """
        Cancel all assigned packings and retry to assign them
        Also try to assign all confirmed packings afterwards
        In case we can assign more moves
        """
        if isinstance(ids, (int, long)):
            ids = [ids]

        domain = [('type', '=', 'out'),
                  ('state', '=', 'assigned')]

        if ids:
            domain += [('ids', 'in', ids)]

        # priority: high number = higher priority
        # try to assign first the high priority pickings
        picking_ids = self.search(
            cr, uid, domain, context=context, order='priority desc')
        canceled_ids = self.cancel_assign(cr, uid, picking_ids)
        assigned_ids = self.action_assign(cr, uid, picking_ids)

        # exclude picking ids because we have already
        # tried to assign them
        if not ids:
            domain = [('type', '=', 'out'),
                      ('state', '=', 'confirmed'),
                      ('id', 'not in', picking_ids)]
            confirmed_ids = self.search(
                cr, uid, domain, context=context, order='priority desc')
            self.action_assign(cr, uid, confirmed_ids)

        return canceled_ids, assigned_ids

StockPicking()


class StockInventory(osv.Model):

    _inherit = "stock.inventory"

    def action_done(self, cr, uid, ids, context=None):
        res = super(StockInventory, self).action_done(
            cr, uid, ids, context=context)
        self.pool.get('stock.picking').retry_assign_all(
            cr, uid, [], context=context)
        return res

StockInventory()
