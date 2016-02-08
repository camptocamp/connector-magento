# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Matthieu Dietrich. Copyright Camptocamp SA
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
{'name': 'Last Purchase Price',
 'version': '1',
 'depends': ['product_get_cost_field',
             'product_cost_incl_bom',
             'product_cost_incl_bom_price_history',
             'product_price_history',
             'sale_markup',
             'stock',
             ],
 'author': 'Camptocamp',
 'description': """
    Compute a new price on product, "Last purchase price" ;
    the goal is to get as this price the last invoiced amount
    when receiving the product. If it is older than a year,
    use the supplier price.
 """,
 'website': 'http://www.camptocamp.com',
 'data': [
     'product_view.xml'
     ],
 'installable': True,
 }
