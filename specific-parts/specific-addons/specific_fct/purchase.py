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

from openerp.osv import orm, fields
from openerp.addons import purchase

# Monkey-patch to allow line deletion in "Waiting approval" state

addons_po_line = purchase.purchase.purchase_order_line


def unlink(self, cr, uid, ids, context=None):
    """
    According to the ticket [REF #398]:
    I comment the line that raise en exception if the line in not
    in state draft or cancel
    """
    procurement_ids_to_cancel = []
    for line in self.browse(cr, uid, ids, context=context):
        # if line.state not in ['draft', 'cancel']:
        #     raise osv.except_osv(
        #         _('Invalid Action!'),
        #         _('Cannot delete a purchase order line'
        #           ' which is in state \'%s\'.')
        #         % (line.state,)
        #     )
        if line.move_dest_id:
            procurement_ids_to_cancel.extend(
                procurement.id for procurement
                in line.move_dest_id.procurements
            )
    if procurement_ids_to_cancel:
        self.pool['procurement.order'].action_cancel(
            cr, uid, procurement_ids_to_cancel
        )
    return super(addons_po_line, self).unlink(cr, uid, ids, context=context)

addons_po_line.unlink = unlink


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    # allow for edition in 'confirmed' state
    _columns = {
        'partner_ref': fields.char(
            'Supplier Reference',
            states={
                'approved': [('readonly', True)],
                'done': [('readonly', True)]
            },
            size=64,
            help="Reference of the sales order or quotation sent by your "
                 "supplier. It's mainly used to do the matching when you "
                 "receive the products as this reference is usually written "
                 "on the delivery order sent by your supplier."
        ),
    }

    def wkf_approve_order(self, cr, uid, ids, context=None):
        # Update product price if dropshipping order is approved
        super(purchase_order, self).wkf_approve_order(
            cr, uid, ids, context=context)
        product_obj = self.pool['product.product']
        for order in self.browse(cr, uid, ids, context=context):
            if order.sale_flow and order.sale_flow == 'direct_delivery':
                for line in order.order_line:
                    product = line.product_id
                    if product.type in ('product', 'consu'):
                        product_obj.write(cr, uid, [product.id],
                                          {'standard_price': line.price_unit},
                                          context=context)
        return True

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """
            Give the tracking number to Magento
            TODO put the change in OCA
        """
        _super = super(purchase_order, self)
        vals = _super._prepare_order_picking(cr, uid, order, context=context)
        if order.sale_flow in ('direct_delivery',
                               'direct_invoice_and_delivery'):
            sale = order.sale_id
            carrier = sale and sale.carrier_id or False
            if carrier:
                vals['carrier_id'] = carrier.id
            # for dropshipping orders, set carrier file as generated
            # (since the delivery / tracking is done by the supplier)
            vals['carrier_file_generated'] = True
        return vals

class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    _order = 'sequence ASC'

    _columns = {
        'sequence': fields.integer('Sequence'),
    }
