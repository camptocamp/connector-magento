# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError


class SupplierImport(Component):
    """ Supplier is an attribute in Magento, imported in magento.supplier """
    _name = 'magento.supplier.importer'
    _inherit = 'magento.importer'
    _apply_on = ['magento.supplier']

    MAGENTO_ATTRIBUTE_ID = 860

    def _get_magento_data(self):
        """ Return the raw Magento data for ``self.magento_id`` """
        backend_adapter = self.component_by_name(
            'magento.product.attribute.adapter')
        options = backend_adapter.options(self.MAGENTO_ATTRIBUTE_ID)
        for option in options:
            if option['value'] == str(self.external_id):
                return option
        raise MappingError('On Magento, the product is configured with a '
                           'supplier having an option with the ID %s, but '
                           'this option does not exist on Magento' %
                           self.external_id)


class DebonixProductSupplierImportMapper(Component):
    _name = 'magento.supplier.import.mapper'
    _inherit = 'magento.import.mapper'
    _apply_on = ['magento.supplier']

    direct = [
        ('label', 'name'),
    ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def odoo_id(self, record):
        partner = self.env['res.partner'].search(
            [('name', '=ilike', record['label']),
             ('supplier', '=', True),
             ('parent_id', '=', False),
             ],
            limit=1,
        )
        if partner:
            return {'odoo_id': partner.id}
