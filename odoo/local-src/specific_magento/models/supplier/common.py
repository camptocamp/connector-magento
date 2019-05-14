# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""

Options of the `openerp_supplier_name` attribute.

When we import a product, the API gives us the ID of the option selected
for the supplier field.  We have to import the options in order to match
the ID with the name of the supplier.

"""

from odoo import fields, models


class MagentoSupplier(models.Model):
    _name = 'magento.supplier'
    _inherit = 'magento.binding'
    _inherits = {'res.partner': 'odoo_id'}
    _description = 'Magento Supplier'

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
        string="Partner",
        required=True,
        oldname='openerp_id',
    )

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, external_id)',
         'A Supplier with same ID on Magento already exists.'),
    ]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    magento_supplier_bind_ids = fields.One2many(
        comodel_name="magento.supplier",
        inverse_name="odoo_id",
        string="Magento Supplier Bindings",
        copy=False,
    )
