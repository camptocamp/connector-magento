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

import pooler
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
        assigned_ids = self.retry_assign(cr, uid, picking_ids, context=context)

        # exclude picking ids because we have already
        # tried to assign them
        if not ids:
            domain = [('type', '=', 'out'),
                      ('state', '=', 'confirmed'),
                      ('id', 'not in', picking_ids)]
            confirmed_ids = self.search(
                cr, uid, domain, context=context, order='priority desc')
            self.retry_assign(cr, uid, confirmed_ids, context=context)

        return canceled_ids, assigned_ids

    def retry_assign(self, cr, uid, ids, context=None):
        assigned_ids = []
        # commit the transaction after each assign
        # otherwise it uses too much locks (_product_reserve)
        local_cr = pooler.get_db(cr.dbname).cursor()
        for picking_id in ids:
            try:
                self.action_assign(local_cr, uid, [picking_id])
                assigned_ids.append(picking_id)
            except osv.except_osv:
                # the action_assign may raise an osv.except
                # when there is no confirmed move line
                # the silent exception is intended
                # as we do not have to assign the picking
                # in such case
                local_cr.rollback()
            else:
                local_cr.commit()

        try:
            local_cr.close()
        except Exception, e:
            pass
        return assigned_ids

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
