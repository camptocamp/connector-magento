# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _

from odoo.addons.component.core import Component


class MoveExpectedDateExport(Component):
    _name = 'magento.debonix.stock.move.exporter'
    _inherit = 'magento.exporter'
    _apply_on = ['stock.move']

    def run(self, move):
        """ Export the new expected date to Magento """
        if not move.exists():
            return
        sale_line = move.sale_line_id
        if not sale_line:
            return
        sale_line_binder = self.binder_for('magento.sale.order.line')
        magento_sale_line_id = sale_line_binder.to_external(
            sale_line.id, wrap=True)
        if not magento_sale_line_id:
            return _('Not a Magento order line')

        adapter = self.component(
            usage='backend.adapter', model_name='magento.sale.order')
        adapter.set_expected_date(
            int(magento_sale_line_id),
            fields.Datetime.to_string(move.date_expected))
