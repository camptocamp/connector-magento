# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2010-2012 Camptocamp SA
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
{
    'name' : 'Product_Equivalences',
    'version' : '1',
    'depends' : ['base',
                 'product',
                 'packing_product_change'],
    'author' : 'Camptocamp',
    'description': """
Simple module which adds an link on products to :
 - an equivalent product
 - a list of compatibles products (no business logic)

If a product has an equivalent, it will be automatically
replaced by its equivalent in outgoing pickings.
    """,
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['product_view.xml',],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
