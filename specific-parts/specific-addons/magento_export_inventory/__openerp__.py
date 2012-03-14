# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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
    'name' : 'Export Inventory Specific',
    'version' : '1',
    'depends' : ['product',
                 'magentoerpconnect',
                 'bom_stock'],
    'author' : 'Camptocamp',
    'license': 'AGPL-3',
    'description': """
Customisation of Magento OpenERP Connector for Debonix.

This module needs modifications on Magento which add some fields to the API.

First, it adds the "Backorders" Strategy which can be chosen
separately on each product.
 - No Negative Stock Allowed
 - Negative Stock Allowed
 - Negative Stock Allowed (but warn customer)

It also uses the bom_stock quantity.
Always put "is_in_stock" to True
And set the value of some additional fields.


    """,
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['product_view.xml', 
                  ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
