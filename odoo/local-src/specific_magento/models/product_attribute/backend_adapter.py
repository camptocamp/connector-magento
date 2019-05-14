# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class AddressAdapter(Component):
    _name = 'magento.product.attribute.adapter'
    _inherit = 'magento.adapter'
    _magento_model = 'catalog_product_attribute'

    def options(self, id):
        return self._call('%s.options' % self._magento_model,
                          [int(id)])
