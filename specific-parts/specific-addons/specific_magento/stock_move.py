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

from datetime import datetime
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.magentoerpconnect.connector import get_environment
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    GenericAdapter,
)
from .backend import magento_debonix
from .related_action import open_direct


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('date_expected'):
            self._on_write_expected_date(cr, uid, ids, vals['date_expected'],
                                         context=context)
        _super = super(stock_move, self)
        return _super.write(cr, uid, ids, vals, context=context)

    def _on_write_expected_date(self, cr, uid, ids, date_expected,
                                context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if context.get('connector_no_export'):
            return
        session = ConnectorSession(cr, uid, context=context)
        for move in self.browse(cr, uid, ids, context=context):
            expected = datetime.strptime(date_expected,
                                         DEFAULT_SERVER_DATETIME_FORMAT)
            previous = datetime.strptime(move.date_expected,
                                         DEFAULT_SERVER_DATETIME_FORMAT)
            if expected.date() == previous.date():
                # only export if the date changed, we don't want to spam
                # with changes of only a few hours
                continue
            picking = move.picking_id
            if not picking:
                continue
            if picking.type != 'out':
                continue
            sale_line = move.sale_line_id
            if not sale_line:
                continue
            for binding in sale_line.magento_bind_ids:
                export_move_expected_date.delay(session,
                                                self._name,
                                                binding.backend_id.id,
                                                move.id)


@job
@related_action(action=open_direct)
def export_move_expected_date(session, model_name, backend_id, record_id):
    """ Export the new expected delivery date of a stock move """
    env = get_environment(session, model_name, backend_id)
    exporter = env.get_connector_unit(MoveExpectedDateExport)
    return exporter.run(record_id)


@magento_debonix
class MoveExpectedDateExport(ExportSynchronizer):
    _model_name = 'stock.move'

    def run(self, record_id):
        """ Export the new expected date to Magento """
        move = self.session.browse(self.model._name, record_id)
        sale_line = move.sale_line_id
        if not sale_line:
            return
        sale = sale_line.order_id
        sale_binder = self.get_binder_for_model('magento.sale.order')
        magento_sale_id = sale_binder.to_backend(sale.id, wrap=True)
        if not magento_sale_id:
            # cannot find the sale for this move, exit
            return
        sale_line_binder = self.get_binder_for_model('magento.sale.order.line')
        magento_sale_line_id = sale_line_binder.to_backend(sale_line.id,
                                                           wrap=True)
        if not magento_sale_line_id:
            return _('Not a Magento order line')

        adapter = self.get_connector_unit_for_model(GenericAdapter,
                                                    'magento.sale.order')
        adapter.set_expected_date(magento_sale_id,
                                  magento_sale_line_id,
                                  move.date_expected)
