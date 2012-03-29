# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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

from osv import osv, fields


class product_product(osv.osv):

    _inherit = 'product.product'

    _columns = {
        'list_price_coefficient':
            fields.float(
                'Sale Price Coefficient',
                 digits=(3, 2),
                 required=True,
                 help="For products imported from the supplier's "
                      "catalog, the sale price is computed:\n"
                      "Supplier list price * Coefficient."),
        }

    _defaults = {
        'list_price_coefficient': lambda *a: 1.0,
        }

product_product()
