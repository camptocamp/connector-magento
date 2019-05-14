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
import logging
import xmlrpclib

from openerp.tools.translate import _
from openerp.addons.connector.exception import FailedJobError
from openerp.addons.magentoerpconnect.stock_picking import (
    MagentoPickingExport,
)
from openerp.addons.magentoerpconnect.stock_tracking import (
    MagentoTrackingExport,
)
from .backend import magento_debonix

_logger = logging.getLogger(__name__)


@magento_debonix
class DebonixMagentoPickingExport(MagentoPickingExport):
    """ Replace the export of pickings.

    Debonix uses a special API that allows to change products in the
    pickings. When a product has been modified, we send the old along
    with the new - delivered - sku.

    --
    Temporary workaround:

    Due to problems with "Packs", the export has been simplified.
    This is only a quick fix before a proper one: they will use "bundle"
    products on Magento.

    Cause:

        A pack named X contains 2 products: Y and Z.
        It is a BoM in OpenERP.
        It is a simple product in Magento and Magento is not aware of Y
        and Z.  When we take on order of product X on Magento, we import
        in, the OpenERP SO has one product X, but the picking has Y and
        Z.  When we want to create the shipment on Magento, if the send
        a partial picking, we have to say which product has been
        delivered, so we send Y to Magento, which in turns say that it
        doesn't have Y in the sale order.

    Workaround resolution:

        When we want to create a partial shipment on Magento, we have to
        send the delivered products. The workaround is to always create
        the full shipment, in that case we don't need to send the list
        of delivered products, Magento just consider all of them as
        delivered.

    Correct solution:

        Use bundle products on Magento, Magento will know which
        components is inside a shipment. It will be done, but meanwhile
        we use the workaround above.

    --

    """
    _model_name = 'magento.stock.picking.out'

    # NOTE: do not migrate it for the moment, to see with the customer
    # def _get_lines_info(self, picking):
    #     skus = []
    #     for line in picking.move_lines:
    #         old_sku = line.old_product_id.default_code
    #         # create a list with all product of the packing
    #         item = {'sku': line.product_id.default_code,
    #                 'qty': line.product_qty,
    #                 }
    #         if old_sku:
    #             item.update({'old_sku': old_sku})
    #         skus.append(item)
    #     return skus

    # NOTE: do not migrate this because we want to handle partial deliveries
    # and this can block the process
    # def _workaround_run(self, binding_id):
    #     picking = self.session.browse(self.model._name, binding_id)
    #     # Ideally we would have to check if another picking has already
    #     # been delivered and in that case, return eagerly. As the pickings
    #     # are exported fully, the second picking has nothing to do.
    #     # But, when this code will be in production, we will have
    #     # pickings which have been partially delivered on Magento and
    #     # we must create the second picking, so in all cases we have
    #     # to try to create it and catch the error if it was already
    #     # delivered.
    #     args = self._get_args(picking, {})
    #     try:
    #         # close is always false, no longer necessary in magento
    #         magento_id = self.backend_adapter.create(*args, close=False)
    #     except xmlrpclib.Fault as err:
    #         # When the shipping is already created on Magento, it returns:
    #         # <Fault 102: u"Impossible de faire l\'exp\xe9dition de la
    #         # commande.">
    #         if err.faultCode == 102:
    #             return _('Canceled: the delivery order already '
    #                      'exists on Magento (fault 102).')
    #         else:
    #             raise
    #     else:
    #         self.binder.bind(magento_id, binding_id)

    # NOTE: do not migrate it for the moment, to see with the customer
    # def run(self, binding_id):
    #     # TODO remove this line when the bundles are used
    #     return self._workaround_run(binding_id)

    #     picking = self.session.browse(self.model._name, binding_id)
    #     lines_info = self._get_lines_info(picking)
    #     args = self._get_args(picking, lines_info)
    #     try:
    #         # close is always false, no longer necessary in magento
    #         magento_id = self.backend_adapter.create(*args, close=False)
    #     except xmlrpclib.Fault as err:
    #         # When the shipping is already created on Magento, it returns:
    #         # <Fault 102: u"Impossible de faire l\'exp\xe9dition de la
    #         # commande.">
    #         if err.faultCode == 102:
    #             return _('Canceled: the delivery order already '
    #                      'exists on Magento (fault 102).')
    #         else:
    #             raise
    #     else:
    #         self.binder.bind(magento_id, binding_id)


@magento_debonix
class DebonixMagentoTrackingExport(MagentoTrackingExport):
    """ This class is part of the temporary workaround for the
    bundle products.

    See the docstring of DebonixMagentoPickingExport
    """

    def _export_tracking_on_first_picking(self, binding, first_binding):
        carrier = binding.carrier_id
        if not carrier:
            return FailedJobError('The carrier is missing on the picking %s.' %
                                  binding.name)
        if not carrier.magento_export_tracking:
            return _('The carrier %s does not export '
                     'tracking numbers.') % carrier.name
        if not binding.carrier_tracking_ref:
            return _('No tracking number to send.')

        sale_binding_id = binding.magento_order_id
        if not sale_binding_id:
            return FailedJobError("No sales order is linked with the picking "
                                  "%s, can't export the tracking number." %
                                  binding.name)
        binder = self.get_binder_for_model()
        magento_id = binder.to_backend(first_binding.id)
        self._validate(binding)
        self._check_allowed_carrier(binding, sale_binding_id.magento_id)
        tracking_args = self._get_tracking_args(binding)
        self.backend_adapter.add_tracking_number(magento_id, *tracking_args)

    def run(self, binding_id):
        binding = self.session.browse(self.model._name, binding_id)

        # When we use partial pickings, we only send the first one
        # as a complete delivery.
        # So when we send the tracking number, we try to find if
        # we have a magento_id on another binding for the same sale
        # order and we send the tracking on this one.
        sale = binding.sale_id
        for picking in sale.picking_ids:
            if picking.id == binding.openerp_id.id:
                continue
            other_bindings = picking.magento_bind_ids
            if other_bindings and other_bindings[0].magento_id:
                self._export_tracking_on_first_picking(binding,
                                                       other_bindings[0])
                break
        else:
            # No existing picking, normal behavior
            return super(DebonixMagentoTrackingExport, self).run(binding_id)
