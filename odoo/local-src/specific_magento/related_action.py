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
from openerp.tools.translate import _


def open_direct(session, job, id_pos=3):
    """ Open a form view with the record.

    :param id_pos: position of the record ID in the args
    """
    model = job.args[0]
    # shift one to the left because session is not in job.args
    record_id = job.args[id_pos - 1]
    action = {
        'name': _('Related Record'),
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
    }
    record = session.browse(model, record_id)
    if not record.exists():
        raise orm.except_orm(_('Error'),
                             _('The record has been deleted'))
    action.update({
        'res_model': model,
        'res_id': record_id,
    })
    return action
