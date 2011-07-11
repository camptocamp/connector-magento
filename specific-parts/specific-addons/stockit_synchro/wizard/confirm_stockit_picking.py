# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Guewen Baconnier (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


# I started this wizard to ask only for costs and set the picking to "done"
# But had issues with osv_memory of v5 which try to create a new line in stock.move.memory.stockit.in
# when we modify a line
# So I stopped the development here, the normal partial_packing will be used even if it asks for quantities


import netsvc
import time
from osv import fields, osv
from tools.translate import _


class StockPartialMemoryIn(osv.osv_memory):
# check at migration to v6 if it can be replaced by the stock.move.memory.in object
    _name = "stock.move.memory.stockit.in"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True),
        'quantity' : fields.float("Quantity", required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'prodlot_id' : fields.many2one('stock.production.lot', 'Production Lot'),
        'move_id' : fields.many2one('stock.move', "Move"),
        'cost' : fields.float("Cost", help="Unit Cost for this product line"),
        'wizard_id' : fields.many2one('stockit.confirm.in.picking', string="Wizard"),
        'currency' : fields.many2one('res.currency', string="Currency", help="Currency in which Unit cost is expressed"),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for record in self.read(cr, uid, ids, ['product_id'], context):
            res.append((record['id'], record['product_id'] ))
        return res

StockPartialMemoryIn()


class StockItConfirmPicking(osv.osv_memory):
    _name = 'stockit.confirm.in.picking'
    _description = 'Input costs of products for PMP and set the picking as done'

    _rec_name = 'date'
    _columns = {
        'date': fields.datetime('Date', required=True),
        'product_moves_in' : fields.one2many('stock.move.memory.stockit.in', 'wizard_id', 'Moves'),
     }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for record in self.read(cr, uid, ids, ['date'], context):
            res.append((record['id'], record['date']))
        return res

    def get_picking_type(self, cr, uid, picking, context=None):
        picking_type = picking.type
        for move in picking.move_lines:
            if picking.type == 'in' and move.product_id.cost_method == 'average':
                picking_type = 'in'
                break
            else:
                picking_type = 'out'
        return picking_type

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        pick_obj = self.pool.get('stock.picking')
        res = super(StockItConfirmPicking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        if not picking_ids:
            return res

        result = []
        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            pick_type = self.get_picking_type(cr, uid, pick, context=context)
            if pick_type != 'in':
                raise osv.except_osv(_('UserError'), _('Wizard only applicable for ingoing packings!'))
            for m in pick.move_lines:
                if m.state in ('done', 'cancel'):
                    continue
                result.append(self.__create_move_memory(m))

        if 'product_moves_in' in fields:
            res.update({'product_moves_in': result})
        if 'date' in fields:
            res.update({'date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(StockItConfirmPicking, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
       
        picking_ids = context.get('active_ids', False)

        if not picking_ids:
            # not called through an action (e.g. buildbot), return the default.
            return result

        _moves_arch_lst = """<form string="%s">
                        <field name="date" invisible="1"/>
                        <separator colspan="4" string="%s"/>
                        <field name="%s" colspan="4" nolabel="1" mode="tree,form" width="550" height="200" ></field>
                        """ % (_('Process Document'), _('Products'), "product_moves_in")
        _moves_fields = result['fields']

        # add field related to picking type only
        _moves_fields.update({
                            'product_moves_in': {'relation': 'stock.move.memory.stockit.in', 'type' : 'one2many', 'string' : 'Product Moves'},
                            })

        _moves_arch_lst += """
                <separator string="" colspan="4" />
                <label string="" colspan="2"/>
                <group col="2" colspan="2">
                <button icon='gtk-cancel' special="cancel"
                    string="_Cancel" />
                <button name="done" string="_Validate"
                    colspan="1" type="object" icon="gtk-go-forward" />
            </group>
        </form>"""
        result['arch'] = _moves_arch_lst
        result['fields'] = _moves_fields
        return result

    def __create_move_memory(self, move):
        move_memory = {
            'product_id': move.product_id.id,
            'quantity': move.product_qty,
            'product_uom': move.product_uom.id,
            'prodlot_id': move.prodlot_id.id,
            'move_id': move.id,
            'cost': move.product_id.standard_price,
        }

        if hasattr(move.picking_id, 'purchase_id') and move.picking_id.purchase_id:
            move_memory.update({'currency': move.picking_id.purchase_id.pricelist_id.currency_id.id,})
        return move_memory


    def done(self, cr, uid, ids, context=None):
        """ Update the costs prices and confirm the packings.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        users_obj = self.pool.get('res.users')
        uom_obj = self.pool.get('product.uom')
        user = users_obj.browse(cr, uid, [uid])[0]
        wf_service = netsvc.LocalService("workflow")

        picking_ids = context.get('active_ids', False)
        confirmation = self.browse(cr, uid, ids[0], context=context)

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            moves_list = confirmation.product_moves_in

            # update prices
            for move in moves_list:
                qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, move.quantity, move.product_id.uom_id.id)

                if qty > 0:
                    new_price = currency_obj.compute(cr, uid, move.currency.id,
                            user.company_id.currency_id.id, move.cost)
                    new_price = uom_obj._compute_price(cr, uid, move.product_uom.id, new_price,
                            move.product_id.uom_id.id)
                    if move.product_id.qty_available <= 0:
                        new_std_price = new_price
                    else:
                        new_std_price = ((move.product_id.standard_price * move.product_id.qty_available)
                                         + (new_price * qty))/(move.product_id.qty_available + qty)

                    import pdb; pdb.set_trace()
                    product_obj.write(cr, uid, [move.product_id.id],
                            {'standard_price': new_std_price})
                    move_obj.write(cr, uid, [move.move_id.id], {'price_unit': new_price})
                
            pick_obj.action_move(cr, uid, [pick.id])
            wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)

        return {'type': 'ir.actions.act_window_close'}


StockItConfirmPicking()
