# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockExportAllMagento(models.TransientModel):
    _name = 'stock.export.all.magento'
    _description = 'Export Stock values for all products'

    check_confirm = fields.Boolean(
        string="Confirm Export",
        default=False,
        help="If the Confirm Export field is set to True, "
             "Stock values for all products will be exported "
             "to Magento."
    )

    @api.model
    def export_stock_all_product_magento(self):
        magento_pp_model = self.env['magento.product.product']
        records = magento_pp_model.search([])
        inventory_fields = (
            'manage_stock',
            'backorders',
            'magento_qty',
        )
        for record in records:
            record.with_delay(
                priority=5).export_inventory(fields=inventory_fields)

    @api.multi
    def action_manual_export(self):
        self.ensure_one()
        if self.check_confirm:
            # We will export all data
            self.export_stock_all_product_magento()
        return True
