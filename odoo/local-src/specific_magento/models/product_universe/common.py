# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models



class MagentoProductUniverse(models.Model):
    _name = 'magento.product.universe'
    _inherit = 'magento.binding'
    _description = 'Magento Product Universe'

    name = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, external_id)',
         'A product universe with same ID on Magento already exists.'),
    ]
