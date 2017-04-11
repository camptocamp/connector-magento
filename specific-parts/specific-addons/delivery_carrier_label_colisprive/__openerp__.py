# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Charline Dumontet. Copyright Camptocamp SA
#    Copyright 2017 Camptocamp SA
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
{'name': 'Colis Prive Labels WebService',
 'version': '1.1',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Others',
 'complexity': "normal",
 'depends': ['base_delivery_carrier_label',
             'base_delivery_carrier_files_document',
             'specific_fct',
             'stockit_synchro',
             'debonix_purchase_edi'],
 'description': """Debonix Specific.

This module generate labels with the 'Colis Prive Webservice'
""",
 'website': 'http://www.camptocamp.com',
 'data': ['data/colis_prive_data.xml',
          'carrier_file_view.xml',
          'stock_view.xml',
          ],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
 'external_dependencies': {
     'python': ['suds'],
 }
 }
