# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from tools.translate import _
from osv import osv


class Product(osv.osv):
    """ Inherit product for small customisations"""

    _inherit = 'product.product'

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}

        # reset the osc_oldid -> it represents the id of the product in the old
        # oscommerce system of debonix
        default['x_magerp_zdbx_osc_oldid'] = False
        default['x_ooor_id'] = False

        return super(Product, self).copy(cr, uid, id, default=default, context=context)

    def _fix_default_code(self, cr, uid, default_code, context=None):
        if not default_code:
            return default_code
        default_code = default_code.strip()
        if ',' in default_code:
            raise osv.except_osv(
                _('Error'),
                _("""The comma character "," in the
                reference is forbidden (%s)""" % default_code))
        return default_code

    def create(self, cr, uid, vals, context=None):
        vals['default_code'] = self._fix_default_code(
            cr, uid, vals.get('default_code', False), context=context)
        return super(Product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals['default_code'] = self._fix_default_code(
            cr, uid, vals.get('default_code', False), context=context)
        return super(Product, self).write(cr, uid, ids, vals, context=context)

Product()
