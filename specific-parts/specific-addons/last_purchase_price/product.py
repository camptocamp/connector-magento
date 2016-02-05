# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Matthieu Dietrich. Copyright Camptocamp SA
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
import decimal_precision as dp
from openerp.addons.product_get_cost_field.product_get_cost_field \
    import product_product as cost_field_product


# Monkey-patch to use last_purchase_price (needed to be used
# by the super() in product_cost_incl_bom)
def _compute_purchase_price(self, cr, uid, ids, context=None):
    if not ids:
        return {}
    if isinstance(ids, (int, long)):
        ids = [ids]
    return self._last_purchase_price(cr, uid, ids, field_name=False,
                                     arg=False, context=context)

cost_field_product._compute_purchase_price = _compute_purchase_price


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def _last_purchase_price(self, cr, uid, ids,
                             field_name, arg, context=None):
        """"Use last invoice price if less than a year ; otherwise,
            use supplier price"""
        res = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        cr.execute("""
            SELECT DISTINCT ON (product_id)
            product_id, price_unit
            FROM account_invoice_line
            LEFT JOIN account_invoice
            ON account_invoice_line.invoice_id = account_invoice.id
            WHERE product_id IN %s
            AND type = 'in_invoice'
            AND state in ('open', 'paid')
            AND price_unit > 0.0
            AND date_invoice >= CURRENT_DATE - INTERVAL '1 year'
            ORDER BY product_id, date_invoice DESC;
        """, (tuple(ids), ))
        invoice_prices = dict(cr.fetchall())
        for product in self.browse(cr, uid, ids, context=context):
            if product.id in invoice_prices:
                res[product.id] = invoice_prices[product.id]
            else:
                # Get supplier price
                res[product.id] = product.seller_ids \
                    and product.seller_ids[0].pricelist_ids \
                    and product.seller_ids[0].pricelist_ids[0].price \
                    or 0.0
        return res

    def _cost_price(self, cr, uid, ids, field_name,
                    arg, context=None):
        return super(ProductProduct, self)._cost_price(
            cr, uid, ids, field_name, arg, context=context)

    def _compute_all_markup(self, cr, uid, ids, field_name,
                            arg, context=None):
        return super(ProductProduct, self)._compute_all_markup(
            cr, uid, ids, field_name, arg, context=context)

    def _get_product3(self, cr, uid, ids, context=None):
        prod_obj = self.pool['product.product']
        res = prod_obj._get_product2(cr, uid, ids, context=context)
        return res

    def _get_product_from_template3(self, cr, uid, ids, context=None):
        prod_obj = self.pool['product.product']
        return prod_obj._get_product_from_template2(cr, uid,
                                                    ids,
                                                    context=context)

    def _get_bom_product3(self, cr, uid, ids, context=None):
        prod_obj = self.pool['product.product']
        res = prod_obj._get_bom_product2(cr, uid, ids, context=context)
        return res

    def _get_product_from_invoice(self, cr, uid, ids, context=None):
        res = set()
        invoice_obj = self.pool['account.invoice']
        prod_obj = self.pool['product.product']
        for invoice in invoice_obj.browse(cr, uid, ids, context=context):
            for line in invoice.invoice_line:
                if line.product_id:
                    res.add(line.product_id.id)
        return prod_obj._get_bom_product3(cr, uid, list(res), context=context)

    def _get_product_from_invoice_line(self, cr, uid, ids, context=None):
        res = set()
        line_obj = self.pool['account.invoice.line']
        prod_obj = self.pool['product.product']
        for line in line_obj.browse(cr, uid, ids, context=context):
            if line.product_id:
                res.add(line.product_id.id)
        return prod_obj._get_bom_product3(cr, uid, list(res), context=context)

    _last_purchase_price_triggers = {
        'account.invoice': (_get_product_from_invoice,
                            ['date_invoice', 'type', 'state'],
                            10),
        'account.invoice.line': (_get_product_from_invoice_line,
                                 ['price_unit', 'product_id'],
                                 10),
    }

    _cost_price_triggers = {
        'product.product': (_get_bom_product3, None, 10),
        'product.template': (_get_product_from_template3, None, 10),
        'mrp.bom': (_get_product3,
                    ['bom_id',
                     'bom_lines',
                     'product_id',
                     'product_uom',
                     'product_qty',
                     'product_uos',
                     'product_uos_qty',
                     ], 10),
        'account.invoice': (_get_product_from_invoice,
                            ['date_invoice', 'type', 'state'],
                            10),
        'account.invoice.line': (_get_product_from_invoice_line,
                                 ['price_unit', 'product_id'],
                                 10),
    }

    _columns = {
        'last_purchase_price': fields.function(
            _last_purchase_price,
            store=_last_purchase_price_triggers,
            string='Last purchase price',
            digits_compute=dp.get_precision('Product Price'),
            help="Last purchase price (used for Cost price)"),
        'cost_price': fields.function(
            _cost_price,
            store=_cost_price_triggers,
            string='Replenishment cost',
            digits_compute=dp.get_precision('Product Price'),
            help="The cost that you have to support in order to produce or "
                 "acquire the goods. Depending on the modules installed, "
                 "this cost may be computed based on various pieces of "
                 "information, for example Bills of Materials or latest "
                 "Purchases. By default, the Replenishment cost is the same "
                 "as the Cost Price."),
        'commercial_margin': fields.function(
            _compute_all_markup,
            string='Margin',
            digits_compute=dp.get_precision('Sale Price'),
            store=_cost_price_triggers,
            multi='markup',
            help='Margin is [ sale_price - cost_price ] (not based on '
                 'historical values)'),
        'markup_rate': fields.function(
            _compute_all_markup,
            string='Markup',
            digits_compute=dp.get_precision('Sale Price'),
            store=_cost_price_triggers,
            multi='markup',
            help='Markup is [ margin / sale_price ] (not based on '
                 'historical values)'),
    }
