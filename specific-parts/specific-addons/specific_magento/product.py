# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012-2014 Camptocamp SA
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

from openerp.tools.translate import _
from openerp.addons.connector.unit.mapper import backend_to_m2o
from openerp.addons.magentoerpconnect.product import (
    ProductImport,
    ProductImportMapper,
    ProductInventoryExport
    )
from .backend import magento_debonix


@magento_debonix
class DebonixProductImport(ProductImport):
    _model_name = ['magento.product.product']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        super(DebonixProductImport, self)._import_dependencies()
        record = self.magento_record
        self._import_dependency(record['marque'],
                                'magento.product.brand')

    def _must_skip(self):
        """ Hook called right after we read the data from the backend.

        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).

        If it returns None, the import will continue normally.

        :returns: None | str | unicode
        """
        if self.magento_record['type_id'] == 'debadvancedconfigurable':
            return _('The configurable product is not imported in OpenERP, '
                     'because only the simple products are used in the sales '
                     'orders.')
        return super(DebonixProductImport, self)._must_skip()


@magento_debonix
class DebonixProductImportMapper(ProductImportMapper):
    _model_name = 'magento.product.product'

    direct = (ProductImportMapper.direct +
              [(backend_to_m2o('marque', binding='magento.product.brand'),
                'product_brand_id'),
               ])


@magento_debonix
class DebonixProductInventoryExport(ProductInventoryExport):
    _model_name = ['magento.product.product']

    def _get_data(self, product, fields):
        data = super(DebonixProductInventoryExport, self)._get_data(
            product, fields)

        if product.manage_stock:
            backorders = product.backorders
            data.update({
                'backorders': self._map_backorders[backorders],
                'is_in_stock': True,
                'use_config_manage_stock': True,
                'manage_stock': True,
                'use_config_min_sale_qty': True,
                'use_config_max_sale_qty': True,
            })
        else:
            data.update({
                'manage_stock': False,
                'use_config_manage_stock': False,
            })
        return data
