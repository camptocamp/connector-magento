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

from tools.translate import _
from osv import osv
from osv import fields


class StockPicking(osv.osv):
    _inherit = "stock.picking"

    def try_action_assign_all(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        domain = [('type', '=', 'out'),
                  ('state', '=', 'confirmed')]

        if ids:
            domain += [('ids', 'in', ids)]

        picking_ids = self.search(cr, uid, domain, order='priority desc')

        assigned_ids = self.action_assign(cr, uid, picking_ids)

        return assigned_ids

StockPicking()
