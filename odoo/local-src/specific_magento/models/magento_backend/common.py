# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import api, models


_logger = logging.getLogger(__name__)


class MagentoBackend(models.Model):
    _inherit = 'magento.backend'

    @api.multi
    def update_product_cost(self):
        mag_product_obj = self.env['magento.product.product']
        products = mag_product_obj.search(
            [('backend_id', 'in', ids)])
        _logger.info('Recompute Magento cost for %d products',
                     len(products))
        products.recompute_magento_cost()
        return True

    @api.model
    def _scheduler_update_product_cost(self, domain=None):
        self._magento_backend(self.update_product_cost, domain=domain)

    @api.multi
    def add_checkpoint(self, record):
        """Deactivate the creation of checkpoint for products and categories
        Debonix uses the 'state' of the products to know if it is ready
        to sell.
        """
        binding_models = [
            'magento.product.product',
            'magento.product.category',
        ]
        if record._name in binding_models:
            return
        return super().add_checkpoint(record)
