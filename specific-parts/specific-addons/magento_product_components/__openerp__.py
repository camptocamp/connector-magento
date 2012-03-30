# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Joël Grand-Guillaume and Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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
{'name' : 'Magento product components',
 'version' : '0.2',
 'author' : 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Others',
 'complexity': "normal",  # easy, normal, expert
 'depends' : ['base', 'magentoerpconnect', 'product', 'mrp'],
 'description': """Create a list of components of products based on BoM
    Only supports one level of components.
    The name of the attribute to synchronize with Magento is defined in settings/external.mappinglines.template.csv""",
 'website': 'http://www.camptocamp.com',
 'update_xml': ['product_view.xml', 
                'settings/external.mappinglines.template.csv',],
 'demo_xml': [],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True}

