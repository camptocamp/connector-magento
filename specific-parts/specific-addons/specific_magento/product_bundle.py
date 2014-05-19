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

    def import_bundle(self, magento_record):
        """ Import the bundle information about a product.

        :param magento_record: product information from Magento
        """
        self.magento_record = magento_record
        self.bundle = record['_bundle_data']
        # bind the magento.bundle.bom on the id of the product
        mag_product_id = magento_record['product_id']
        binder = self.get_binder_for_model('magento.bundle.bom')
        binding_id = binder.to_openerp(mag_product_id)
        bom_values = self._bom_values(binding_id)
        if binding_id:
            self.session.write('magento.product.bom', binding_id, bom_values)
        else:
            self.session.create('magento.product.bom', bom_values)

    def _bom_values(self, binding_id):
        mag_product_id = self.magento_record['product_id']
        backend_id = self.backend_record.id
        values = {'magento_id': mag_product_id,
                  'backend_id': backend_id,
                  'product_id': self.binder.to_openerp(mag_product_id,
                                                       unwrap=True),
                  'product_qty': 1,
                  'type': 'phantom',  # TODO: could be normal or phantom
                  }
        lines = []
        for option in self.bundle['options']:
            for selection in option['selections']:
                lines.append(self._selection_values(selection))
        if binding_id:
            lines_product_ids = [line[2]['product_id'] for line in lines]
            # remove deleted lines
            binding = self.session.browse('magento.bundle.bom', binding_id)
            removed_ids = self.session.search(
                'magento.bundle.bom.product',
                [('product_id', 'not in', lines_product_ids),
                 ('backend_id', '=', backend_id),
                 ('bom_id', '=', binding.openerp_id.id)
                 ])
            for removed in self.session.browse('magento.bundle.bom.product',
                                               removed_ids):
                lines.append((2, removed.openerp_id.id))  # unlink the record

        values['bom_lines'] = lines
        return values

    def _selection_values(self, selection):
        mag_product_id = selection['product_id']
        binder = self.get_binder_for_model('magento.bundle.bom.product')
        binding_id = binder.to_openerp(mag_product_id)

        values = {'magento_id': mag_product_id,
                  'backend_id': self.backend_record.id,
                  'product_id': self.binder.to_openerp(selection['product_id'],
                                                       unwrap=True),
                  'product_qty': selection['selection_qty'],
                  'type': 'normal',
                  }
        if binding_id:
            return (1, binding_id, values)
        else:
            return (0, 0, values)


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
