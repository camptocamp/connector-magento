# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from odoo import _, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def write(self, vals):
        if vals.get('date_expected'):
            self._on_write_expected_date(vals['date_expected'])
        return super().write(vals)

    @api.multi
    def _on_write_expected_date(self, date_expected):
        if self.env.context.get('connector_no_export'):
            return
        for move in self:
            expected = fields.Datetime.from_string(date_expected)
            previous = move.date_expected
            if expected.date() == previous.date():
                # only export if the date changed, we don't want to spam
                # with changes of only a few hours
                continue
            picking = move.picking_id
            if not picking:
                continue
            if picking.picking_type_code != 'out':
                continue
            sale_line = move.sale_line_id
            if not sale_line:
                continue
            for binding in sale_line.magento_bind_ids:
                move.with_delay().export_move_expected_date()

    @job(default_channel='root.magento')
    @api.multi
    def export_move_expected_date(self):
        self.ensure_one()
        backend = self.env['magento.backend'].search([], limit=1)
        with backend.work_on(self._name) as work:
            exporter = work.component(usage='record.exporter')
            exporter.run(self)
