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

import netsvc

from tools.translate import _
from osv.orm import Model
from osv import fields


class sale_order(Model):

    _inherit = "sale.order"

    def _invoice_date_get(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            res[id] = False
        cr.execute("SELECT rel.order_id,MIN(inv.date_invoice) FROM sale_order_invoice_rel rel \
        JOIN account_invoice inv ON (rel.invoice_id=inv.id) WHERE rel.order_id IN %s \
        GROUP BY rel.order_id", (tuple(ids),))
        for line in cr.fetchall():
            res[line[0]] = line[1]
        return res

    def _invoiced_date_search(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        new_args = []
        ids = []
        for argument in args:
            operator = argument[1]
            value = argument[2]
            cr.execute("SELECT rel.order_id FROM sale_order_invoice_rel rel \
            JOIN account_invoice inv ON (rel.invoice_id=inv.id) WHERE inv.date_invoice IS NOT NULL AND \
            inv.date_invoice " + operator + " %s", (str(value),))
            for line in cr.fetchall():
                ids.append(line[0])
        if ids:
            new_args.append(('id', 'in', ids))
        return new_args

    _columns = {
        'date_invoiced': fields.function(_invoice_date_get, method=True, fnct_search=_invoiced_date_search,
            type='date', string='Invoice Date', help="Date of the first invoice generated for this SO"),
    }

    def _skip_draft_invoice(self, cr, uid, invoice):
        """
        Open invoices directly (bypass draft) when created from an order
        Specific customisation to avoid the manual confirmation of the invoice
        when the invoice is created from the order.
        """
        if invoice.state == 'draft':
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice',
                                    invoice.id, 'invoice_open', cr)

    def _add_extra_picking_lines(self, cr, uid, ids, invoice, grouped=False):
        """
        Lines in pickings which are not in the sale order are considered
        as gift. They have to be added on the invoice with a 0 price unit.
        """
        picking_obj = self.pool.get('stock.picking')
        invoice_line_obj = self.pool.get('account.invoice.line')

        # when there are new gift products in a picking,
        # they have to be added on the invoice with 0 price unit
        if invoice.type == 'out_invoice':
            for so in self.browse(cr, uid, ids):
                # products in sale orders
                so_products = []
                for line in so.order_line:
                    if line.product_id:
                        so_products.append(line.product_id.id)

                # products in stock pickings
                for picking in so.picking_ids:

                    partner = picking.address_id and \
                              picking.address_id.partner_id

                    for move_line in picking.move_lines:
                        if move_line.state == 'cancel':
                            continue
                        product = move_line.old_product_id or \
                                  move_line.product_id

                        # filter out products of the sale order
                        if product.id in so_products:
                            continue

                        origin = 'GIFT:' + picking.name

                        if grouped:
                            name = (picking.name or '') + '-' + move_line.name
                        else:
                            name = move_line.name

                        account_id = move_line.product_id.product_tmpl_id.\
                                property_account_income.id
                        if not account_id:
                            account_id = move_line.product_id.categ_id.\
                                    property_account_income_categ.id

                        tax_ids = picking_obj._get_taxes_invoice(
                            cr, uid, move_line, invoice.type)
                        account_analytic_id = \
                            picking_obj._get_account_analytic_invoice(
                                cr, uid, picking, move_line)

                        uos_id = move_line.product_uos and \
                                 move_line.product_uos.id or False
                        if not uos_id:
                            uos_id = move_line.product_uom.id
                        fisc_pos_obj = self.pool.get('account.fiscal.position')
                        account_id = fisc_pos_obj.map_account(
                            cr, uid,
                            partner.property_account_position,
                            account_id)
                        note = _("This product has been "
                                 "added in the delivery order %s") % \
                               (picking.name,)
                        invoice_line_id = invoice_line_obj.create(cr, uid,
                            {'name': name,
                             'origin': origin,
                             'invoice_id': invoice.id,
                             'uos_id': uos_id,
                             'product_id': move_line.product_id.id,
                             'account_id': account_id,
                             'price_unit': 0.0,
                             'discount': 0.0,
                             'quantity': move_line.product_uos_qty or
                                         move_line.product_qty,
                             'invoice_line_tax_id': [(6, 0, tax_ids)],
                             'account_analytic_id': account_analytic_id,
                             'note': note,
                            })
                        picking_obj._invoice_line_hook(
                            cr, uid, move_line, invoice_line_id)

    def action_invoice_create(self, cr, uid, ids, grouped=False,
                              states=['confirmed', 'done', 'exception'],
                              date_inv=False, context=None):
        """
        Inherit legacy method to :
         - skip the draft state on the invoices created from the order
         - add pickings lines not in the so as gifts on the invoice
        """
        invoice_id = super(sale_order, self).action_invoice_create(
            cr, uid, ids, grouped=grouped, states=states,
            date_inv=date_inv, context=context)
        if invoice_id:
            invoice = self.pool.get('account.invoice').browse(
                cr, uid, invoice_id, context=context)

            self._skip_draft_invoice(cr, uid, invoice)

            self._add_extra_picking_lines(cr, uid, ids, invoice, grouped=grouped)

        return invoice_id


class sale_order_line(Model):

    _inherit = 'sale.order.line'

    def _prepare_order_line_invoice_line(self, cr, uid, line,
                                         account_id=False, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sale order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           Override the method to add an invoice line with the replaced
           product in the related packing
           Keep the price of the original product but use the accounts of the
           replacement product
           Add a comment which indicates the modification

           Override of the method in order to:
           Empty the "note" field

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        vals = super(sale_order_line, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=account_id, context=context)
        vals['note'] = False
        return vals

