# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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

from openerp.osv import orm, fields


class sale_order(orm.Model):

    _inherit = 'sale.order'

    _columns = {
        'sms_phone': fields.char('SMS Phone', size=10),
    }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        vals = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        # amounts must only apply on the first packing of the order
        # if it is a cash on delivery
        model_data_obj = self.pool['ir.model.data']
        _, product_id = model_data_obj.get_object_reference(
            cr, uid, 'connector_ecommerce', 'product_product_cash_on_delivery')
        if [line.product_id.id == product_id for line in order.order_line]:
            vals.update({
                'cash_on_delivery_amount': order.amount_total,
                'cash_on_delivery_amount_untaxed': order.amount_untaxed,
            })
        vals['sms_phone'] = order.sms_phone
        return vals
