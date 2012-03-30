# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Camptocamp
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
{'name' : 'Supplier Price Update',
 'version' : 'version',
 'author' : 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'version',
 'complexity': "normal",
 'depends' : ['product'],
 'description': """
       This module update pricelist using Import/Export wizards. This concern the update of supplier info part
       of the product form (where we can set price / quantity). The match of the product are made on the product id.
       It can also update the ean13 and the product code.
       
       This two wizard are for 
       1) To export the current product price list
       2) To import the new product price list and update ean13 / code
              
       Export/import is available in CSV or Excel. 
       Excel needs PyExcelerator.""",
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': ['wizard/export_pricelist_view.xml',
                'wizard/import_pricelist_view.xml'],
 'demo_xml': [],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True}

