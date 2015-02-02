# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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
{'name': 'Stock Values at Date',
 'version': '1.2',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Others',
 'complexity': "normal",
 'depends': ['stock',
             ],
 'description': """Debonix Specific.

Add a wizard to export the stock value for each product in a location at
a given date.  The data is exported as a CSV file
""",
 'website': 'http://www.camptocamp.com',
 'data': ['wizard/stock_values_view.xml'],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
 }
