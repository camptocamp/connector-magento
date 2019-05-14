# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class FidelityLineBuilder(Component):
    """ Build a sales order line with a negative amount and a service
    product for a discount.

    This line has a 19.6% tax, it will work only if all the products of
    the sale order have the same tax percentage!

    This is specific to debonix for this reason, debonix sells only
    products with the same tax (20% actually).

    The Magento API has to provide the fields ::

    fidelity_points_balance -> quantity of points used on the sale order
    base_fidelity_currency_amount -> amount of the discount

    Magento provides a taxes included amount, so the FIDELITY product has
    to be configured with a taxes include tax.
    """
    _name = 'magento.order.line.fidelity.builder'
    _inherit = 'ecommerce.order.line.builder'
    _apply_on = ['magento.sale.order']

    def __init__(self, work_context):
        super(FidelityLineBuilder, self).__init__(work_context)
        self.product_ref = ('specific_magento',
                            'product_product_debonix_fidelity')
        self.sign = -1
        self.points = None

    def get_line(self):
        line = super(FidelityLineBuilder, self).get_line()
        if self.points:
            line['name'] = "%s %s" % (self.points, line['name'])
        return line


class AdminCostsLineBuilder(Component):
    """ Build a sales order line with positive amount for administrative costs.

    The Magento API has to provide the field ::

    base_xipaymentrules_fees_amount -> amount of the costs (tax included)

    Magento provides a taxes included amount, so the ADMIN product has
    to be configured with a taxes include tax.
    """
    _name = 'magento.order.line.admincosts.builder'
    _inherit = 'ecommerce.order.line.builder'
    _apply_on = ['magento.sale.order']

    def __init__(self, work_context):
        super().__init__(work_context)
        self.product_ref = ('specific_magento',
                            'product_product_debonix_admin_costs')
