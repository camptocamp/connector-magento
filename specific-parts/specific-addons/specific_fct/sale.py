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

from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp import netsvc


class sale_order(orm.Model):

    _inherit = "sale.order"

    def _invoice_date_get(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            res[id] = False
        if not ids:
            return res
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
        'date_invoiced': fields.function(
            _invoice_date_get,
            fnct_search=_invoiced_date_search,
            type='date',
            string='Invoice Date',
            help="Date of the first invoice generated for this SO"),
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

    def _add_extra_picking_lines(self, cr, uid, ids, invoice, grouped=False,
                                 context=None):
        """
        Lines in pickings which are not in the sale order are considered
        as gift. They have to be added on the invoice with a 0 price unit.
        """
        picking_obj = self.pool.get('stock.picking')
        invoice_line_obj = self.pool.get('account.invoice.line')

        # when there are new gift products in a picking,
        # they have to be added on the invoice with 0 price unit
        if invoice.type == 'out_invoice':
            for so in self.browse(cr, uid, ids, context=context):
                # products in sale orders
                so_products = []
                for line in so.order_line:
                    if line.product_id:
                        so_products.append(line.product_id.id)

                # products in stock pickings
                for picking in so.picking_ids:

                    partner = picking.partner_id

                    for move_line in picking.move_lines:
                        if move_line.state == 'cancel':
                            continue
                        product = move_line.old_product_id or \
                                  move_line.product_id

                        # filter out products of the sale order
                        if product.id in so_products:
                            continue

                        origin = _('GIFT:') + picking.name

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
                            {'name': '\n'.join([name, note]),
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
                            })
                        picking_obj._invoice_line_hook(
                            cr, uid, move_line, invoice_line_id)

    def action_invoice_create(self, cr, uid, ids, grouped=False,
                              states=['confirmed', 'done', 'exception'],
                              date_invoice=False, context=None):
        """
        Inherit legacy method to :
         - skip the draft state on the invoices created from the order
         - add pickings lines not in the so as gifts on the invoice
        """
        invoice_id = super(sale_order, self).action_invoice_create(
            cr, uid, ids, grouped=grouped, states=states,
            date_invoice=date_invoice, context=context)
        if invoice_id:
            invoice = self.pool.get('account.invoice').browse(
                cr, uid, invoice_id, context=context)

            self._skip_draft_invoice(cr, uid, invoice)

            self._add_extra_picking_lines(cr, uid, ids, invoice,
                                          grouped=grouped, context=context)

        return invoice_id


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False,
                          context=None):
        """ They don't want the full sale description in the line's description
        but only the product's name.
        """
        result = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom, qty_uos=0,
            uos=uos, name=name, partner_id=partner_id, lang=lang,
            update_tax=update_tax, date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)

        if not product:
            return result

        product_obj = self.pool['product.product']
        product_name = product_obj.name_get(cr, uid, [product],
                                            context=context)[0][1]
        result['value']['name'] = product_name
        return result

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        ## Recompute markup_rate and commercial_margin on duplicate
        # see : https://trello.com/c/iCCivgv6/346-quand-on-duplique-une-commande-annulee-la-marge-n-est-pas-recalculee
        current_sale_order_line = self.browse(cr, uid, id, context=context)
        localcontext = context.copy()
        localcontext.update(
            {
                'product_id': current_sale_order_line.product_id and current_sale_order_line.product_id.id or False,
                'price_unit': current_sale_order_line.price_unit,
                'discount': current_sale_order_line.discount,
                'product_uom': current_sale_order_line.product_uom and current_sale_order_line.product_uom.id or False,
                'pricelist': current_sale_order_line.order_id.pricelist_id and current_sale_order_line.order_id.pricelist_id.id or False,
                'markup_rate': current_sale_order_line.markup_rate,
                'commercial_margin': current_sale_order_line.commercial_margin,
            }
        )
        res = self.onchange_price_unit(cr, uid, [id], override_unit_price=True, context=localcontext)
        if res['value']:
            # If price was changed because of sale_floor_price
            if res['value']['price_unit'] > current_sale_order_line.price_unit:
                default['price_unit'] = res['value']['price_unit']
            default['markup_rate'] = res['value']['markup_rate']
            if 'commercial_margin' in res['value']:
                default['commercial_margin'] = res['value']['commercial_margin']
        return super(sale_order_line, self).copy_data(cr, uid, id, default=default,
                                                      context=context)
