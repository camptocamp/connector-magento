# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """HACK to fix issue https://github.com/OCA/bank-payment/issues/536

        When generating the invoices, Odoo overrides the payment mode (at
        least) as it calls once again '_onchange_partner_id'.
        """
        if self.env.context.get('keep_sale_order_payment_mode'):
            payment_mode = self.payment_mode_id
        res = super()._onchange_partner_id()
        if self.env.context.get('keep_sale_order_payment_mode'):
            self.payment_mode_id = payment_mode
        return res
