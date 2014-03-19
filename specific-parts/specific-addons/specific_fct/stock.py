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

from openerp import netsvc

from openerp.tools.translate import _
from openerp.osv import orm, fields


class StockPicking(orm.Model):

    _inherit = "stock.picking"

    # Debonix want them sorted in this order
    _order = 'priority desc, min_date asc, date asc'

    def get_selection_priority(self, cr, uid, context=None):
        """ Rename the priorities to match what Debonix is used to.

        That means Low, Normal, Urgent instead of Normal, Urgent, Very Urgent.

        """
        mapping = {'0': 'Low', '1': 'Normal', '2': 'Urgent'}
        selection = super(StockPicking, self).get_selection_priority(
            cr, uid, context=context)
        return [(key, mapping.get(key, name)) for key, name in selection]

    def __selection_priority(self, cr, uid, context=None):
        """ Do not touch me. Extend `get_selection_priority` to modify
        the selection
        """
        return self.get_selection_priority(cr, uid, context=context)

    _columns = {
        'priority': fields.selection(__selection_priority,
                                     'Priority',
                                     required=True,
                                     select=True,  # add an index for the sort
                                     help='The priority of the picking'),
    }

    _defaults = {
        'priority': '1',  # normal priority
    }

    # TODO maybe useless, see in stock_picking_priority
    def try_action_assign_all(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        domain = [('type', '=', 'out'),
                  ('state', '=', 'confirmed')]

        if ids:
            domain += [('ids', 'in', ids)]

        picking_ids = self.search(cr, uid, domain, order='priority desc')

        return self.retry_assign(cr, uid, picking_ids)
