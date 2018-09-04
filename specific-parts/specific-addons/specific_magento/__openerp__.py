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

{'name': 'Magento Connector Customization',
 'version': '1.1',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Connector',
 'depends': ['magentoerpconnect',
             'mrp',
             'product_brand',
             'base_transaction_id',
             'delivery_carrier_file_chronopost',
             'base_transaction_id',
             'product_cost_incl_bom',  # for cost_price, lp:margin-analysis
             'packing_product_change',  # lp:c2c-ecom-addons
             'l10n_fr_intrastat_product',  # lp:new-report-intrastat
             ],
 'description': """
Magento Connector Customization
===============================

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['magento_data.xml',
          'product_data.xml',
          'product_view.xml',
          'magento_model_view.xml',
          'security/ir.model.access.csv',
          'wizard/export_all_stock_view.xml',
          'cron_data.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }