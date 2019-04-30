# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class DebonixMagentoInvoiceListener(Component):
    """Switch off the creation of binding for the invoice,
    debonix doesn't want to export invoices because they are
    always created on Magento before the import of the sales orders.
    If a magento.account.invoice binding record is created manually,
    it will still be exported though.
    """
    _inherit = 'magento.account.invoice.listener'

    def on_invoice_paid(self, record):
        # NOTE: disabled
        pass

    def on_invoice_validated(self, record):
        # NOTE: disabled
        pass
