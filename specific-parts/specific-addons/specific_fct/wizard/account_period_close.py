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


class account_period_close(orm.TransientModel):
    _inherit = 'account.period.close'

    def data_save(self, cr, uid, ids, context=None):
        """
        Override the method not to block if the period contains draft
        move lines
        """
        mode = 'done'
        for form in self.read(cr, uid, ids, context=context):
            if form['sure']:
                for id in context['active_ids']:
                    cr.execute('update account_journal_period set '
                               'state=%s where period_id=%s',
                               (mode, id))
                    cr.execute('update account_period set state=%s '
                               'where id=%s', (mode, id))

        return {'type': 'ir.actions.act_window_close'}
