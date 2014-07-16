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
from openerp.osv import orm

_logger = logging.getLogger(__name__)


class StockPicking(orm.Model):

    _inherit = "stock.picking"

    _defaults = {
        'number_of_packages': 1,
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

        picking_ids = self.search(cr, uid, domain, context=context)

        for picking_id in picking_ids:
            try:
                self.action_assign(cr, uid, [picking_id], context)
            except orm.except_orm:
                # ignore the error, the picking will just stay as confirmed
                name = self.read(cr, uid, picking_id, ['name'],
                                 context=context)['name']
                _logger.info('error in action_assign for picking %s',
                             name, exc_info=True)
        return True
