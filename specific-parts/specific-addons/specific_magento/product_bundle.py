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
from openerp.osv import orm, fields
from openerp.addons.magentoerpconnect.product import BundleImporter
from .backend import magento_debonix


_logger = logging.getLogger(__name__)


@magento_debonix
class BoMBundleImporter(BundleImporter):
    """ Import bundle products as Bill of Materials.

    Only import the "group" of products. Ignore
    options such as special prices.

    Called at the end of the import of a product.
    """
    _model_name = 'magento.product.product'

    def run(self, magento_record):
        """ Import the bundle information for a product.

        :param magento_record: product information from Magento
        """
        self.magento_record = magento_record
        _logger.info('Importing bundle information for Magento product %s',
                     magento_record['product_id'])
        self.bundle = magento_record['_bundle_data']
        binding_id = self._import_bom()
        self._import_selections(binding_id)

    def _import_bom(self):
        # bind the magento.bundle.bom on the id of the product
        mag_product_id = self.magento_record['product_id']
        binder = self.get_binder_for_model('magento.bundle.bom')
        bom_values = self._bom_values()
        binding_id = binder.to_openerp(mag_product_id)
        if binding_id:
            self.session.write('magento.bundle.bom', binding_id, bom_values)
            _logger.info('magento.bundle.bom %d updated', binding_id)
        else:
            binding_id = self.session.create('magento.bundle.bom', bom_values)
            _logger.info('magento.bundle.bom %d created', binding_id)
        return binding_id

    def _bom_values(self):
        magento_product_id = self.magento_record['product_id']
        values = {'backend_id': self.backend_record.id,
                  'product_qty': 1,
                  'type': 'normal',
                  }
        values.update(self._common_product_values(magento_product_id))
        return values

    def _import_selections(self, bom_binding_id):
        existing_product_ids = []
        binder = self.get_binder_for_model('magento.bundle.bom.product')
        for option in self.bundle['options']:
            for selection in option['selections']:
                values = self._selection_values(bom_binding_id, selection)
                existing_product_ids.append(values['product_id'])
                prod_binding_id = binder.to_openerp(values['magento_id'])

                if prod_binding_id:
                    self.session.write('magento.bundle.bom.product',
                                       prod_binding_id, values)
                    _logger.info('magento.bundle.bom.product %d updated',
                                 prod_binding_id)
                else:
                    new_id = self.session.create('magento.bundle.bom.product',
                                                 values)
                    _logger.info('magento.bundle.bom.product %d created',
                                 new_id)

        bom_binder = self.get_binder_for_model('magento.bundle.bom')
        # remove deleted components
        removed_ids = self.session.search(
            'magento.bundle.bom.product',
            [('product_id', 'not in', existing_product_ids),
             ('backend_id', '=', self.backend_record.id),
             ('bom_id', '=', bom_binder.unwrap_binding(bom_binding_id))
             ])
        bundle_product_binder = self.get_binder_for_model(
            'magento.bundle.bom.product')
        for removed in self.session.browse('magento.bundle.bom.product',
                                           removed_ids):
            removed_id = bundle_product_binder.unwrap_binding(removed.id)
            self.session.unlink('mrp.bom', [removed_id])
            _logger.info('magento.bundle.bom.product %d removed', removed.id)

    def _common_product_values(self, magento_product_id):
        product_id = self.binder.to_openerp(magento_product_id,
                                            unwrap=True)
        product = self.session.read('product.product', product_id,
                                    ['uom_id', 'name'])
        values = {
            'magento_id': magento_product_id,
            'product_id': product_id,
            'name': product['name'],
            'product_uom': product['uom_id'][0],
        }
        return values

    def _selection_values(self, bom_binding_id, selection):
        magento_product_id = selection['product_id']
        bom_binder = self.get_binder_for_model('magento.bundle.bom')
        values = {'backend_id': self.backend_record.id,
                  'product_qty': selection['selection_qty'],
                  'type': 'normal',
                  'bom_id': bom_binder.unwrap_binding(bom_binding_id),
                  }
        values.update(self._common_product_values(magento_product_id))
        return values


class magento_bundle_bom(orm.Model):
    _name = 'magento.bundle.bom'
    _inherit = 'magento.binding'
    _inherits = {'mrp.bom': 'openerp_id'}
    _description = 'Magento Bundle (BoM)'

    _columns = {
        'openerp_id': fields.many2one('mrp.bom',
                                      string='Bill of Material',
                                      required=True,
                                      ondelete='cascade'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A product brand with same ID on Magento already exists.'),
    ]


class magento_bundle_bom_product(orm.Model):
    _name = 'magento.bundle.bom.product'
    _inherit = 'magento.binding'
    _inherits = {'mrp.bom': 'openerp_id'}
    _description = 'Magento Bundle Product (BoM)'

    _columns = {
        'openerp_id': fields.many2one('mrp.bom',
                                      string='Bill of Material',
                                      required=True,
                                      ondelete='cascade'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A product brand with same ID on Magento already exists.'),
    ]
