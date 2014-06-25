# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
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
{'name': 'specific_fct',
 'version': '1',
 'depends': ['account',
             'product',
             'stock',
             'sale',
             'sale_stock',
             'packing_product_change',
             'on_inventory_retry_assign',
             'account_statement_base_completion',
             'connector_ecommerce',
             'server_environment',
             'import_tracking',
             ],
 'author': 'Camptocamp',
 'description': """Code customisation module

Changes:

Add column reconcile_partial_id on account.move.line tree to be able to
differenciate them at first glance
 """,
 'website': 'http://www.camptocamp.com',
 'data': ['account_invoice_action_data.xml',
          'product_view.xml',
          'sale_view.xml',
          'account_view.xml',
          'account_invoice_view.xml',
          'partner_view.xml',
          'stock_view.xml',
          'security/ir.model.access.csv',
          'security/security.xml',
          'data_completion.xml',
          'company_view.xml',
          'wizard/stock_partial_picking_view.xml',
          ],
 'installable': True,
}
