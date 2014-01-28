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

{
     "name" : "Specific for Magento",
     "version" : "1.0",
     "author" : "Camptocamp",
     'license': 'AGPL-3',
     "category" : "Generic Modules/Others",
     "description":
"""
All the specific customisations which concerns the magento connector
""",
     "website": "http://camptocamp.com",
     "depends" : ['base',
                  'magentoerpconnect',
                  ],
     "init_xml" : [],
     "demo_xml" : [],
     "update_xml" : [
        'product_view.xml',
        'sale_view.xml',
        'settings/external.mappinglines.template.csv',
        'settings/magerp.product_category_attribute_options.csv',
        'magento_data.xml',
                    ],
     "active": False,
     'installable': False
}
