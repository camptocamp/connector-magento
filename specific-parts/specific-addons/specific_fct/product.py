# -*- encoding: utf-8 -*-
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

import netsvc
import time

from osv import fields, osv
from tools.translate import _
from magentoerpconnect import magerp_osv

class Product(magerp_osv.magerp_osv):
    " Inherit product for small customisations"
    _inherit = 'product.product'

    _columns = {
        'to_deactivate': fields.boolean('To deactivate', help="If checked, on the next Export catalog, the product will be deactivated on Magento and then on OpenERP. If an open picking using this product exists on OpenERP, the product will not be deactivated before the next Export catalog.")
    }

    _defaults = {
        'product_type':lambda * a:'simple'
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        if not default:
            default = {}
            
        # reset the osc_oldid -> it represents the id of the product in the old
        # oscommerce system of debonix
        default['x_magerp_zdbx_osc_oldid'] = False
        default['x_ooor_id'] = False
        
        return super(Product, self).copy(cr, uid, id, default=default, context=context)   

    def try_deactivate_product(self, cr, uid, ids, context):
        # we have to avoid to deactivate products used in pickings to not block them
        product_ids = ids[:]
        products_not_to_deactivate = []
        stock_move_obj = self.pool.get('stock.move')
        # get opened stock moves using a product to deactivate
        moves = stock_move_obj.search(cr, uid, [('product_id', 'in', ids), ('state', 'not in', ('cancel', 'done'))], context=context)
        for move in stock_move_obj.browse(cr, uid, moves, context=context):
            products_not_to_deactivate.append(move.product_id.id)
        # keep only unique ids
        products_not_to_deactivate = list(set(products_not_to_deactivate))
        # remove products used by stock moves from the products to deactivate
        [product_ids.remove(id) for id in products_not_to_deactivate]
        self.write(cr, uid, product_ids, {'active': False} , context=context)
        return True

Product()


class magerp_product_attributes(magerp_osv.magerp_osv):
    """ Inherit magerp.product_attributes in order to add attributes to hide
        from the product screen """
    _inherit = 'magerp.product_attributes'
    
    def __init__(self, pool, cr):
        """ Add attribute codes in the list of hidden attributes """
        super(magerp_product_attributes, self).__init__(pool, cr)
        self._no_create_list.extend([
                                    'zdbx_default_ean13',
                                    'zdbx_default_code',
                                    'zdbx_default_set_pack',
                                    'zdbx_default_sku_coffrets',
                                    'fupid',
                                    'mpid',
                                    'rdcategories', # replaced by magento_rdc_category on product.category
                                    ])
                                        
magerp_product_attributes()


class ProductCategory(magerp_osv.magerp_osv):
    """Modify the available magento sorting options."""
    _inherit = "product.category"

    def _recursive_rdc_category_id(self, cr, uid, id, context=None):
        """ Return the Rue Du Commerce Category of the category.
        Search recursively from the bottom of the tree"""
        category = self.browse(cr, uid, id, context=context)
        if category.magento_rdc_category:
            res = category.magento_rdc_category.id
        else:
            if category.parent_id:
                res = self._recursive_rdc_category_id(cr, uid, category.parent_id.id, context)
            else:
                res = False
        return res

    def _get_magento_rdc_category_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            res[id] = self._recursive_rdc_category_id(cr, uid, id, context)
        return res

    SORT_BY_OPTIONS = (
        ('None', 'Use Config Settings'),
        ('position', 'Position'),
        ('price', 'Price'),
        ('zdbx_default_marque', 'Manufacturer'),
        ('pyksel_rdc_availability', 'Availability'),
    )
    
    _columns = {
        'available_sort_by': fields.selection(
                            SORT_BY_OPTIONS,
                            'Available Product Listing (Sort By)',
                            size=32),
        'default_sort_by': fields.selection(
                            SORT_BY_OPTIONS,
                            'Default Product Listing Sort (Sort By)',
                            size=32),
        'magento_rdc_category': fields.many2one('magerp.product_attribute_options', 'Rue Du Commerce Category', domain="[('attribute_id','=',268)]", ondelete="set null", help="Rue Du Commerce category applied on products of this category."),
        'magento_rdc_category_default': fields.function(_get_magento_rdc_category_id, type='many2one', obj='magerp.product_attribute_options', method=True, string='Rue Du Commerce Parent Category')
    }

    def write_now_on_category_products(self, cr, uid, ids, magento_rdc_category_id, context=None):
        """ We have to update the products on Magento. So we put the write_date to now() on products which are in or below the
         category. To limit the number of products to update, we select only the products of the child categories which have the same
         Rue du commerce category (so the ones that have been impacted)."""
        cat_products_ids = self.pool.get('product.product').search(cr, uid, [('categ_id','child_of',[ids])], context=context) # all the products of the category and childs
        product_ids_to_update = []
        # We check each product to see wether it use an other rdc category
        # It's a bit expensive in term of performance but the most products we can exclude from the export catalog of magento, the
        # better it is, so we have advantage of loss some time here but gain in export catalog
        for product in self.pool.get('product.product').browse(cr, uid, cat_products_ids, context):
            if product.categ_id.magento_rdc_category_default.id == magento_rdc_category_id:
                product_ids_to_update.append(product.id)

        cr.execute("update product_product set write_date = now() where id in %s", (tuple(product_ids_to_update),))
        return True

    def create(self, cr, uid, vals, context=None):
        category_id = super(ProductCategory, self).create(cr, uid, vals, context)
        if 'magento_rdc_category' in vals:
            self.write_now_on_category_products(cr, uid, category_id, vals['magento_rdc_category'], context)
        return category_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(ProductCategory, self).write(cr, uid, ids, vals, context)
        if 'magento_rdc_category' in vals:
            self.write_now_on_category_products(cr, uid, ids, vals['magento_rdc_category'], context)
        return res

ProductCategory()