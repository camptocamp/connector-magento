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

import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict
import pooler

import wizard
from osv import osv
import tools
from tools.translate import _

_moves_arch = UpdateableStr()
_moves_fields = UpdateableDict()

_moves_arch_end = '''<?xml version="1.0"?>
<form string="Packing result">
    <label string="The packing has been successfully made !" colspan="4"/>
    <field name="back_order_notification" colspan="4" nolabel="1"/>
</form>'''
_moves_fields_end = {
    'back_order_notification': {'string':'Back Order' ,'type':'text', 'readonly':True}
                     }

def make_default(val):
    def fct(uid, data, state):
        return val
    return fct

def _to_xml(s):
    return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def _get_moves(self, cr, uid, data, context):
    pick_obj = pooler.get_pool(cr.dbname).get('stock.picking')
    pick = pick_obj.browse(cr, uid, [data['id']], context)[0]
    res = {}

    _moves_fields.clear()
    _moves_arch_lst = ['<?xml version="1.0"?>', '<form string="Make packing">']

    for m in pick.move_lines:
        if m.state in ('done', 'cancel'):
            continue
        quantity = m.product_qty
        if m.state<>'assigned':
            quantity = 0

        _moves_arch_lst.append('<field name="move%s" />' % (m.id,))
        _moves_fields['move%s' % m.id] = {
                'string': _to_xml(m.name),
                'type' : 'float', 'required' : True, 'default' : make_default(quantity)}

        _moves_arch_lst.append('<newline/>')
        res.setdefault('moves', []).append(m.id)

    _moves_arch_lst.append('</form>')
    _moves_arch.string = '\n'.join(_moves_arch_lst)
    return res

def _do_split(self, cr, uid, data, context):
    move_obj = pooler.get_pool(cr.dbname).get('stock.move')
    pick_obj = pooler.get_pool(cr.dbname).get('stock.picking')
    pick = pick_obj.browse(cr, uid, [data['id']])[0]
    new_picking = None
    new_moves = []

    complete, too_many, too_few = [], [], []
    pool = pooler.get_pool(cr.dbname)
    for move in move_obj.browse(cr, uid, data['form'].get('moves',[])):
        if move.product_qty == data['form']['move%s' % move.id]:
            complete.append(move)
        elif move.product_qty > data['form']['move%s' % move.id]:
            too_few.append(move)
        else:
            too_many.append(move)

    for move in too_few:
        if not new_picking:

            new_picking = pick_obj.copy(cr, uid, pick.id,
                    {
                        'name': pool.get('ir.sequence').get(cr, uid, 'stock.picking'),
                        'move_lines' : [],
                        'state':'draft',
                    })
        if data['form']['move%s' % move.id] <> 0:
            new_obj = move_obj.copy(cr, uid, move.id,
                {
                    'product_qty' : data['form']['move%s' % move.id],
                    'product_uos_qty':data['form']['move%s' % move.id],
                    'picking_id' : new_picking,
                    'state': 'assigned',
                    'move_dest_id': False,
                    'price_unit': move.price_unit,
                })
        move_obj.write(cr, uid, [move.id],
                {
                    'product_qty' : move.product_qty - data['form']['move%s' % move.id],
                    'product_uos_qty':move.product_qty - data['form']['move%s' % move.id],
                })

    if new_picking:
        move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
        for move in too_many:
            move_obj.write(cr, uid, [move.id],
                    {
                        'product_qty' : data['form']['move%s' % move.id],
                        'product_uos_qty': data['form']['move%s' % move.id],
                        'picking_id': new_picking,
                    })
    else:
        for move in too_many:
            move_obj.write(cr, uid, [move.id],
                    {
                        'product_qty': data['form']['move%s' % move.id],
                        'product_uos_qty': data['form']['move%s' % move.id]
                    })

    # assign the backorder
    if new_picking:
        pick_obj.write(cr, uid, [pick.id], {'backorder_id': new_picking})

    if new_picking:
        pick_obj.write(cr, uid, [pick.id], {'backorder_id': new_picking})
        pick_obj.draft_force_assign(cr, uid, [new_picking])
    else:
        pick_obj.draft_force_assign(cr, uid, [pick.id])

    bo_name = ''
    if new_picking:
        bo_name = pick_obj.read(cr, uid, [new_picking], ['name'])[0]['name']
    return {'new_picking':new_picking or False, 'back_order':bo_name}

def _get_default(self, cr, uid, data, context):
    if data['form']['back_order']:
        data['form']['back_order_notification'] = _('Back Order %s Assigned to this Packing.') % (tools.ustr(data['form']['back_order']),)
    return data['form']

class partial_picking_no_confirm(wizard.interface):

    states = {
        'init': {
            'actions': [ _get_moves ],
            'result': {'type': 'form', 'arch': _moves_arch, 'fields': _moves_fields,
                'state' : (
                    ('end', 'Cancel'),
                    ('split', 'Make Picking')
                )
            },
        },
        'split': {
            'actions': [ _do_split ],
            'result': {'type': 'state', 'state': 'end2'},
        },
        'end2': {
            'actions': [ _get_default ],
            'result': {'type': 'form', 'arch': _moves_arch_end,
                'fields': _moves_fields_end,
                'state': (
                    ('end', 'Close'),
                )
            },
        },
    }

partial_picking_no_confirm('stock.partial_picking_no_confirm')
