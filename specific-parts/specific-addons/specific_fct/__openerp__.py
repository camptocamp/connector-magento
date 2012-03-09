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
{
    'name' : 'specific_fct',
    'version' : '1',
    'depends' : ['base',
                 'account',
                 'product',
                 'purchase',
                 'base_sale_multichannels',
                 'magentoerpconnect',
                 'stock',
                 'c2c_bom_stock',
                 'c2c_magento_set_and_pack_product',
                 'c2c_magento_product_components',
                 'sale',
                 # 'sale_markup',
                 # 'sale_floor_price',
                 'account_statement_import',
                 'c2c_pack_product_chg',
                 'c2c_magento_equivalences',
                 "mrp",
                 "base_module_record",
                 "point_of_sale",
                 ],
    'author' : 'Camptocamp',
    'description': """Code customisation module""",
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['product_view.xml',
                   'settings/external.mappinglines.template.csv',
                   'sale_view.xml',
                   'account_invoice_view.xml',
                   'partner_view.xml',
                   'wizard.xml',
                   'stock_view.xml',
                   'security/security.xml',
                   'statement_view.xml',
                   'account_view.xml'
                  ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
