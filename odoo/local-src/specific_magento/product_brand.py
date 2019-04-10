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

from openerp.osv import orm, fields
from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  )
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    MagentoImportSynchronizer,
    )
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    MagentoCRUDAdapter,
    )
from .backend import magento_debonix


class magento_product_brand(orm.Model):
    _name = 'magento.product.brand'
    _inherit = 'magento.binding'
    _inherits = {'product.brand': 'openerp_id'}
    _description = 'Magento Product Brand'

    _columns = {
        'openerp_id': fields.many2one('product.brand',
                                      string='Product Brand',
                                      required=True,
                                      ondelete='cascade'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A product brand with same ID on Magento already exists.'),
    ]


class product_brand(orm.Model):
    _inherit = 'product.brand'

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.product.brand', 'openerp_id',
            string="Magento Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['magento_bind_ids'] = False
        return super(product_brand, self).copy_data(cr, uid, id,
                                                    default=default,
                                                    context=context)


@magento_debonix
class ProductBrandImport(MagentoImportSynchronizer):
    """ Brand is an attribute in Magento, imported in product_brand """
    _model_name = ['magento.product.brand']

    MAGENTO_ATTRIBUTE_ID = 206

    def _get_magento_data(self):
        """ Return the raw Magento data for ``self.magento_id`` """
        backend_adapter = self.get_connector_unit_for_model(
            MagentoCRUDAdapter, 'magento.product.attribute')
        options = backend_adapter.options(self.MAGENTO_ATTRIBUTE_ID)
        for option in options:
            if option['value'] == str(self.magento_id):
                return option
        raise MappingError('On Magento, the product is configured with a '
                           'brand ("marque" attribute) having an option with '
                           'the ID %s, but this option does not exist '
                           'on Magento' % self.magento_id)


@magento_debonix
class DebonixProductBrandImportMapper(ImportMapper):
    _model_name = 'magento.product.brand'

    direct = [('label', 'name'),
              ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
