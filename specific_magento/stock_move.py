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

from openerp.addons.connector.event import on_record_write
from openerp.addons.connector.exception import IDMissingInBackend
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.magentoerpconnect.connector import get_environment
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    GenericAdapter,
)
from openerp.addons.magentoerpconnect.related_action import unwrap_binding
from .backend import magento_debonix
from .related_action import open_direct


@on_record_write(model_names='stock.move')
def move_write(session, model_name, record_id, vals):
    if session.context.get('connector_no_export'):
        return
    if not vals.get('date_expected'):
        return
    move = session.browse(model_name, record_id)
    picking = move.picking_id
    if not picking:
        return
    if picking.type != 'out':
        return
    sale_line = move.sale_line_id
    if not sale_line:
        return
    for binding in sale_line.magento_bind_ids:
        # TODO set delay
        export_move_expected_date.delay(session,
                                        model_name,
                                        binding.backend_id.id,
                                        record_id)


@job
@related_action(action=open_direct)
def export_move_expected_date(session, model_name, backend_id, record_id):
    """ Export the new expected delivery date of a stock move """
    move = session.browse(model_name, record_id)
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
        product_binder = self.get_binder_for_model('magento.product.product')
        if not sale_line.product_id:
            return
        magento_product_id = product_binder.to_backend(sale_line.product_id.id,
                                                       wrap=True)
        if not magento_product_id:
            raise IDMissingInBackend

        adapter = self.get_connector_unit_for_model(GenericAdapter,
                                                    'magento.sale.order')
        adapter.set_expected_date(magento_sale_id,
                                  magento_product_id,
                                  move.date_expected)
