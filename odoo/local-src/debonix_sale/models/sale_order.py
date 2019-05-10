# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """HACK to fix issue https://github.com/OCA/bank-payment/issues/536

        See the 'AccountInvoice._onchange_partner_id' docstring of this module.
        """
        self = self.with_context(keep_sale_order_payment_mode=True)
        # NOTE: the new 'self' is correctly sent in the 'super()' call
        inv_ids = super().action_invoice_create(grouped, final)
        return inv_ids
