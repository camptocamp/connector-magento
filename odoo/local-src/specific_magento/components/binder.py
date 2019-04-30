# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector_magento.components.binder import MagentoModelBinder


class DebonixBinder(Component):
    _inherit = 'magento.binder'

    _apply_on = MagentoModelBinder._apply_on + [
        'magento.product.brand',
        'magento.supplier',
        'magento.product.universe',
        # TODO: bundle not migrated, waiting customer answer
        # 'magento.bundle.bom',
        # 'magento.bundle.bom.product',
    ]
