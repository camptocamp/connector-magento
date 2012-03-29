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
    'name' : 'external_supplier_catalog',
    'version' : '1.0',
    'depends' : ['product',],
    'author' : 'Camptocamp',
    'description': """Mapping between external categories and OpenERP categories per supplier.
Coefficient on each external category / product.
Sale price is computed as purchase price * product's coefficient.

Designed only to be used with Kettle to import / update products.

If a product does not exists, its coefficient is determined from the external category.
Otherwise, its coefficient is never updated.
""",
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['product_view.xml',
                   'supplier_catalog_category_view.xml',
                  ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
