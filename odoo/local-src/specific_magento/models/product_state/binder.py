# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
"""

Options of the `openerp_state` attribute.

When we import a product, the API gives us the ID of the option selected
for the state field.  We have to import the options in order to match
the name of the state with the state of the field.

"""

from odoo.addons.component.core import Component


class ProductStateBinder(Component):
    """ 'Fake' binder: hard code bindings for the product states

    ``openerp_state`` is an attribute on Magento, with options.
    Each option on Magento is an ID, with a textual value.

    The options are::

        draft: 811
        obsolete: 809
        sellable: 810

    """
    _name = 'magento.product.state.binder'
    _inherit = ['magento.binder']
    _apply_on = [
        'magento.product.state',
    ]

    magento_bindings = {811: 'draft', 809: 'obsolete', 810: 'sellable'}
    # inverse mapping
    odoo_bindings = dict((v, k) for k, v in magento_bindings.items())

    def to_internal(self, external_id, unwrap=False):
        return self.magento_bindings[int(external_id)]

    # NOTE: binding parameter has been renamed binding_state
    # here for clarity purpose
    def to_external(self, binding_state, wrap=False):
        return self.odoo_bindings[binding_state]

    def bind(self, external_id, binding):
        raise TypeError('%s cannot be synchronized' % self._model._name)
