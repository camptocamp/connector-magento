# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError


class ProductBrandImporter(Component):
    """ Brand is an attribute in Magento, imported in product_brand """
    _name = 'magento.product.brand.importer'
    _inherit = 'magento.importer'
    _apply_on = ['magento.product.brand']

    MAGENTO_ATTRIBUTE_ID = 206

    def _get_magento_data(self):
        """ Return the raw Magento data for ``self.external_id`` """
        backend_adapter = self.component_by_name(
            'magento.product.attribute.adapter')
        options = backend_adapter.options(self.MAGENTO_ATTRIBUTE_ID)
        for option in options:
            if option['value'] == str(self.external_id):
                return option
        raise MappingError('On Magento, the product is configured with a '
                           'brand ("marque" attribute) having an option with '
                           'the ID %s, but this option does not exist '
                           'on Magento' % self.external_id)


class DebonixProductBrandImportMapper(Component):
    _name = 'magento.product.brand.import.mapper'
    _inherit = 'magento.import.mapper'
    _apply_on = ['magento.product.brand']

    direct = [
        ('label', 'name'),
    ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
