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

    def allow_automatic_merge(self, cr, uid, procurement, po_vals,
                              line_vals, context=None):
        # redefining function from sale_dropshipping
        sogedesca_ids = self.pool['res.partner'].search(
            cr, uid, [('edifact_message', '=', True)], context=context)
        if po_vals.get('dest_address_id', False) and \
           po_vals.get('partner_id', False) in sogedesca_ids:
            return True
        return super(ProcurementOrder, self).allow_automatic_merge(
            cr, uid, procurement, po_vals, line_vals, context=context)

    def _product_virtual_get(self, cr, uid, order_point):
        # Since some manual orders could be confirmed,
        # we return None if a PO has the orderpoint's product in its lines
        product_id = order_point.product_id.id
        po_lines = self.pool['purchase.order.line'].search(
            cr, uid,
            [('product_id', '=', product_id),
             ('order_id.state', '=', 'confirmed')],
            context={})
        if len(po_lines) > 0:
            return None
        return super(ProcurementOrder, self)._product_virtual_get(
            cr, uid, order_point)

    def create_automatic_op(self, cr, uid, use_new_cursor=False, context=None):
        # Add a flag to context (see product.py) in order to skip products
        # with open POs
        if context is None:
            context = {}
        context.update({'automatic_op_skip_po': True})
        return super(ProcurementOrder, self).create_automatic_op(
            cr, uid, use_new_cursor, context=context)
