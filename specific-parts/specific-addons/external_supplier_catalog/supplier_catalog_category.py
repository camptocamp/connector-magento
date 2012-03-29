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

from osv import osv, fields


class supplier_catalog_category(osv.osv):

    _name = 'supplier.catalog.category'

    _description = "Supplier Catalog Categories"

    _columns = {
        'supplier_code':
            fields.selection(
                (('toolstream', 'Toolstream'),),
                'Supplier Code',
                required=True),
        'name':
            fields.char("Supplier's Category Code", size=30, required=True),
        'category_id':
            fields.many2one('product.category', 'Category', required=True),
        'price_coefficient':
            fields.float('Price Coefficient', digits=(3,2), required=True),
    }

    _defaults = {
        'price_coefficient':lambda *a: 1.0,
    }

supplier_catalog_category()


class product_category(osv.osv):

    _inherit = 'product.category'

    _columns = {
        'supplier_catalog_category_ids':
            fields.one2many('supplier.catalog.category',
                            'category_id',
                            'Supplier Catalog Categories'),
        }

product_category()
