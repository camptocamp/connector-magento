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

from openerp.addons.magentoerpconnect.stock_picking import (
    StockPickingAdapter,
)

from .backend import magento_debonix

_logger = logging.getLogger(__name__)


@magento_debonix
class DebonixStockPickingAdapter(StockPickingAdapter):
    _model_name = 'magento.stock.picking.out'

    def create(self, order_id, items, comment, email, include_comment,
               close=False):
        """ Create a record on the external system """
        _logger.info('Export a delivery order with: '
                     '%s.creer(%s)',
                     self._magento_model,
                     unicode([order_id, items, comment, email,
                              include_comment, close]))
        return self._call('%s.creer' % self._magento_model,
                          [order_id, items, comment, email,
                           include_comment, close])
