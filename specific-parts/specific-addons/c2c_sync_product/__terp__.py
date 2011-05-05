# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright Camptocamp SA
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

{
    'name': 'Product synchronization through csv',
    'version': '0.2',
    'category': 'Generic Modules/Others',
    'description': """
      This module allow to synchronize product through csv files. It match the code of the product
      to update or create the it in the company DB.
      
      Assumption: The synchronized product have a unique code in the company. The taxes are the following:
        - Sale : code = 01
        - Purchase : code = 05
    """,
    'author': 'camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': ['product','stock'],
    'init_xml': [],
    'update_xml': [
                   'wizard/c2c_sync_product_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
