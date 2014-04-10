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

from openerp.addons.magentoerpconnect.stock_picking import (
    StockPickingAdapter,
    MagentoPickingExport,
)
from .backend import magento_debonix

_logger = logging.getLogger(__name__)


@magento_debonix
class DebonixMagentoPickingExport(MagentoPickingExport):
    """ Replace the export of pickings.

    Debonix uses a special API that allows to change products in the
    pickings. When a product has been modified, we send the old along
    with the new - delivered - sku.

    """
    _model_name = 'magento.stock.picking.out'

    def _get_lines_info(self, picking):
        skus = []
        for line in picking.move_lines:
            old_sku = line.old_product_id.default_code

            # create a list with all product of the packing
            item = {'sku': line.product_id.default_code,
                    'qty': line.product_qty,
                    }
            if old_sku:
                item.update({'old_sku': old_sku})
            skus.append(item)
        return skus

    def run(self, binding_id):
        picking = self.session.browse(self.model._name, binding_id)
        lines_info = self._get_lines_info(picking)
        args = self._get_args(picking, lines_info)
        try:
            # close is always false, no longer necessary in magento
            magento_id = self.backend_adapter.create(*args, close=False)
        except xmlrpclib.Fault as err:
            # When the shipping is already created on Magento, it returns:
            # <Fault 102: u"Impossible de faire l\'exp\xe9dition de la commande.">
            if err.faultCode == 102:
                raise NothingToDoJob('Canceled: the delivery order already '
                                     'exists on Magento (fault 102).')
            else:
                raise
        else:
            self.binder.bind(magento_id, binding_id)


@magento_debonix
class DebonixStockPickingAdapter(StockPickingAdapter):
    _model_name = 'magento.stock.picking.out'

    def create(self, order_id, items, comment, email, include_comment,
               close=False):
        """ Create a record on the external system """
        return self._call('%s.creer' % self._magento_model,
                          [order_id, items, comment, email,
                           include_comment, close])
