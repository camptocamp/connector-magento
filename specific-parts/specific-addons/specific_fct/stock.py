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

    # Debonix want them sorted in this order
    _order = 'priority desc, min_date asc, date asc'

    def retry_assign_all(self, cr, uid, ids, context=None):
        canceled_ids, assigned_ids = super(StockPicking, self).retry_assign_all(
            cr, uid, ids, context=context)
        # try to assign confirmed pickings (those that were not assigned
        # before but can maybe be assigned now)
        # exclude picking_ids because we have already
        # tried to assign them
        if not ids:
            all_ids = (canceled_ids or []) + (assigned_ids or [])
            domain = [('type', '=', 'out'),
                      ('state', '=', 'confirmed'),
                      ('id', 'not in', all_ids)]
            confirmed_ids = self.search(
                cr, uid, domain, context=context, order='priority desc')
            _logger.info('try to assign %d more pickings', len(confirmed_ids))
            for picking_id in confirmed_ids:
                try:
                    assigned_id = self.action_assign(cr, uid, [picking_id],
                                                     context)
                    assigned_ids.append(assigned_id)
                except orm.except_orm as exc:
                    # ignore error, the picking will just stay as
                    # confirmed
                    name = self.read(cr, uid, picking_id, ['name'],
                                     context=context)['name']
                    _logger.info('error in action_assign for picking %s',
                                 name, exc_info=True)
        return canceled_ids, assigned_ids

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

    def try_action_assign_all(self, cr, uid, ids=None, context=None):
        if not ids:
            ids = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        domain = [('type', '=', 'out'),
                  ('state', '=', 'confirmed')]
        if ids:
            domain += [('id', 'in', ids)]

        picking_ids = self.search(cr, uid, domain,
                                  order='priority desc, min_date, date')

        self.retry_assign_all(cr, uid, picking_ids, context=context)
        return True
