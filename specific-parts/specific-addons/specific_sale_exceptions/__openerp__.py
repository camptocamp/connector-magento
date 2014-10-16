# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012-2014 Camptocamp SA
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

{'name' : 'Specific Sale Exceptions',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Generic Modules/Sale',
 'complexity': "easy",
 'depends': ['sale_exceptions',
             'sale_markup',
             ],
 'description': """Custom and specific exceptions for the sale workflow""",
 'website': 'http://www.camptocamp.com',
 'data': ['sale_exception_data.xml',
          'res_partner_view.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
