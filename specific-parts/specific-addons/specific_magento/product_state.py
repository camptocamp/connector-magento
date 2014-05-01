# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


"""

Options of the `openerp_state` attribute.

When we import a product, the API gives us the ID of the option selected
for the state field.  We have to import the options in order to match
the name of the state with the state of the field.

"""

from openerp.addons.magentoerpconnect.unit.binder import (
    MagentoBinder,
)
from .backend import magento_debonix


@magento_debonix
class ProductStateBinder(MagentoBinder):
    """ 'Fake' binder: hard code bindings for the product states

    ``openerp_state`` is an attribute on Magento, with options.
    Each option on Magento is an ID, with a textual value.

    The options are::

        draft: 811
        obsolete: 809
        sellable: 810

    """
    _model_name = 'magento.product.state'

    magento_bindings = {811: 'draft', 809: 'obsolete', 810: 'sellable'}
    # inverse mapping
    openerp_bindings = dict((v, k) for k, v in magento_bindings.iteritems())

    def to_openerp(self, external_id, unwrap=False):
        return self.magento_bindings[int(external_id)]

    def to_backend(self, binding_id, wrap=False):
        return self.openerp_bindings[binding_id]

    def bind(self, external_id, binding_id):
        raise TypeError('%s cannot be synchronized' % self._model._name)
