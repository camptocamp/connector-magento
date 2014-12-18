# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm


class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    # Add context for ir.actions.server call
    def action_cancel(self, cr, uid, ids, context=None):
        if context and \
           context.get('cancel_procurements_act_server', False) and \
           'active_ids' in context:
            ids = context['active_ids']
        return super(ProcurementOrder, self).action_cancel(cr, uid, ids)
