# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class MagentoProductBrand(models.Model):
    _name = 'magento.product.brand'
    _inherit = 'magento.binding'
    _inherits = {'product.brand': 'odoo_id'}
    _description = 'Magento Product Brand'

    odoo_id = fields.Many2one(
        comodel_name="product.brand",
        ondelete="cascade",
        string="Product Brand",
        required=True,
        oldname='openerp_id',
    )

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, external_id)',
         'A product brand with same ID on Magento already exists.'),
    ]


class ProductBrand(models.Model):
    _inherit = 'product.brand'

    magento_bind_ids = fields.One2many(
        comodel_name="magento.product.brand",
        inverse_name="odoo_id",
        string="Magento Bindings",
        copy=False,
    )
