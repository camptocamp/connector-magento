# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class MagentoProductProduct(models.Model):
    _inherit = 'magento.product.product'

    magento_cost = fields.Float(
        string="Computed Cost",
        help="Last computed cost to send on Magento.",
    )
    magento_universe_id = fields.Many2one(
        comodel_name="magento.product.universe",
        ondelete="restrict",
        string=u"Magento Universe",
    )
    universe = fields.Char(
        string="Magento Universe",
        compute='_compute_universe',
        store=True,
    )

    @api.multi
    @api.depends('magento_universe_id.name')
    def _compute_universe(self):
        """ Used in SQL views """
        for product in self:
            product.universe = product.magento_universe_id.name or 'Non défini'

    @api.model
    def product_type_get(self):
        selection = super().product_type_get()
        if 'bundle' not in [item[0] for item in selection]:
            selection.append(('bundle', 'Bundle'))
        return selection

    @api.multi
    def recompute_magento_cost(self):
        for product in self.read(['standard_price', 'magento_cost']):
            new_cost = product['standard_price']
            if new_cost != product['magento_cost']:
                product.magento_cost = new_cost
        return True


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    # indicates that the record has been created from Magento
    # using the `openerp_supplier_*` fields
    from_magento = fields.Boolean(
        default=False,
        readonly=True,
    )
