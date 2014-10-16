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


"""

Options of the `openerp_supplier_name` attribute.

When we import a product, the API gives us the ID of the option selected
for the supplier field.  We have to import the options in order to match
the ID with the name of the supplier.

"""

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


class magento_supplier(orm.Model):
    _name = 'magento.supplier'
    _inherit = 'magento.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'Magento Supplier'

    _columns = {
        'openerp_id': fields.many2one('res.partner',
                                      string='Partner',
                                      required=True,
                                      ondelete='cascade'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A Supplier with same ID on Magento already exists.'),
    ]


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'magento_supplier_bind_ids': fields.one2many(
            'magento.supplier', 'openerp_id',
            string="Magento Supplier Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['magento_supplier_bind_ids'] = False
        return super(res_partner, self).copy_data(cr, uid, id,
                                                  default=default,
                                                  context=context)


@magento_debonix
class SupplierImport(MagentoImportSynchronizer):
    """ Supplier is an attribute in Magento, imported in magento.supplier """
    _model_name = ['magento.supplier']

    MAGENTO_ATTRIBUTE_ID = 860

    def _get_magento_data(self):
        """ Return the raw Magento data for ``self.magento_id`` """
        backend_adapter = self.get_connector_unit_for_model(
            MagentoCRUDAdapter, 'magento.product.attribute')
        options = backend_adapter.options(self.MAGENTO_ATTRIBUTE_ID)
        for option in options:
            if option['value'] == str(self.magento_id):
                return option
        raise MappingError('On Magento, the product is configured with a '
                           'supplier having an option with the ID %s, but '
                           'this option does not exist on Magento' %
                           self.magento_id)


@magento_debonix
class DebonixProductBrandImportMapper(ImportMapper):
    _model_name = 'magento.supplier'

    direct = [('label', 'name'),
              ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def openerp_id(self, record):
        partner_ids = self.session.search(
            'res.partner',
            [('name', '=ilike', record['label']),
             ('supplier', '=', True),
             ('parent_id', '=', False),
             ],
        )
        if partner_ids:
            return {'openerp_id': partner_ids[0]}
