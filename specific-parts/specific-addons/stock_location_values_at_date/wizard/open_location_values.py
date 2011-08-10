# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

import wizard
import time

from tools.translate import _

def _action_open_window(self, cr, uid, data, context):
    cr.execute('select id, name from ir_ui_view where model=%s and type=%s', ('stock.location', 'tree'))
    view_res = cr.fetchone()
    name = _("Locations's Values to %s") % (data['form']['to_date'] or time.strftime('%Y-%m-%d %H:%M:%S'),)
    if data['form']['to_date']:
        name += ''
    return {
        'name': name,
        'view_id': view_res,
        'view_type': 'form',
        "view_mode": 'tree',
        'res_model': 'stock.location',
        'type': 'ir.actions.act_window',
        'context': {'to_date': data['form']['to_date']},
    }


class location_values_at_date(wizard.interface):
    form = '''<?xml version="1.0"?>
    <form string="View Stock Values of Locations">
        <separator string="Stock Location Values At Date" colspan="4"/>
        <field name="to_date"/>
        <newline/>
        <label string=""/>
        <label string="(Keep empty to open the current situation. Adjust HH:MM:SS to 23:59:59 to filter all resources to the 'To' date)" align="0.0" colspan="3"/>
    </form>'''
    form_fields = {
             'to_date': {
                'string': 'To',
                'type': 'datetime',
        },
    }

    states = {
      'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': form, 'fields': form_fields,
                       'state': [('end', 'Cancel','gtk-cancel'), ('open', 'Open Locations','gtk-ok')]}
        },
    'open': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_window, 'state': 'end'}
        }
    }

location_values_at_date('stock.location.values.date')
