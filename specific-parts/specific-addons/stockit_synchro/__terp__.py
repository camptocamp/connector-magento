# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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
    "name": "Stock-it synchro",
    "version": "1.0",
    "depends": ['base',
                'product',
                'stock',
                'delivery',
                'product_multi_ean',
                'c2c_magento_packing_priority',
                ],
    "author": "Camptocamp",
    "description": """Synchro with stock-it (stock management)
    """,
    "website": "http://www.camptocamp.com",
    "category": "Synchronisation",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": ['stockit_data.xml',
                   'stock_workflow.xml',
                   'wizard/product_export_view.xml',
                   'wizard/ean_export_view.xml',
                   'wizard/out_picking_export_view.xml',
                   'wizard/in_picking_export_view.xml',
                   'wizard/in_picking_import_view.xml',
                   'wizard/inventory_import_view.xml',
                   'stockit_menu.xml',
                   'company_view.xml',
                   'stock_view.xml',
                   ],
    "installable": True,
    "active": False,
}
