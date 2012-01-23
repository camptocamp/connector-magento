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
        'to_deactivate': fields.boolean('To deactivate', help="If checked, on the next Export catalog, the product will be deactivated on Magento and then on OpenERP. If an open picking using this product exists on OpenERP, the product will not be deactivated before the next Export catalog."),
        'bom_ids': fields.one2many('mrp.bom','product_id','BoMs'),
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
        cr.commit()
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('default_code', False):
            vals['default_code'] = vals['default_code'].strip()
        return super(Product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('default_code', False):
            vals['default_code'] = vals['default_code'].strip()
        return super(Product, self).write(cr, uid, ids, vals, context=context)

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
                                    'soldes_qty',
                                    'cdiscount_sku',
                                    ])
                                        
magerp_product_attributes()


class ProductCategory(magerp_osv.magerp_osv):
    """Modify the available magento sorting options."""
    _inherit = "product.category"

    def _recursive_category_ids(self, cr, uid, id, field_names, context=None):
        """ Return the Rue Du Commerce / Outilmania Categories of the category.
        Search recursively from the bottom of the tree"""
        category = self.browse(cr, uid, id, context=context)
        res = {}
        if category.magento_rdc_category and 'magento_rdc_category_default' in field_names:
            res['magento_rdc_category_default'] = category.magento_rdc_category.id
            field_names.remove('magento_rdc_category_default')
        if category.magento_omcategory_id and 'magento_omcategory_default_id' in field_names:
            res['magento_omcategory_default_id'] = category.magento_omcategory_id.id
            field_names.remove('magento_omcategory_default_id')

        if field_names:
            if category.parent_id:
                res.update(self._recursive_category_ids(cr, uid, category.parent_id.id, field_names, context))
        return res

    def _get_magento_category_ids(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            res_id = dict((field, False) for field in field_name)
            res_id.update(self._recursive_category_ids(cr, uid, id, field_name[:], context))
            res[id] = res_id
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
        'magento_omcategory_id': fields.many2one('magerp.product_attribute_options', 'Outilmania category', domain="[('attribute_id','=',302)]", ondelete="set null",
                                                         help="Outilmania category applied on products of this category."),
        'magento_rdc_category_default': fields.function(_get_magento_category_ids, type='many2one', obj='magerp.product_attribute_options', method=True, string='Rue Du Commerce Parent Category', multi='magento_categories'),
        'magento_omcategory_default_id': fields.function(_get_magento_category_ids, type='many2one', obj='magerp.product_attribute_options', method=True, string='OutilMania Parent Category', multi='magento_categories'),
        }

    def write_now_on_category_products(self, cr, uid, ids, magento_rdc_category_id, magento_omcategory_id, context=None):
        """ We have to update the products on Magento. So we put the write_date to now() on products which are in or below the
         category. To limit the number of products to update, we select only the products of the child categories which have the same
         Rue du commerce category (so the ones that have been impacted)."""
        cat_products_ids = self.pool.get('product.product').search(cr, uid, [('categ_id','child_of',[ids])], context=context) # all the products of the category and childs
        product_ids_to_update = []
        # We check each product to see wether it use an other rdc category
        # It's a bit expensive in term of performance but the most products we can exclude from the export catalog of magento, the
        # better it is, so we have advantage of loss some time here but gain in export catalog
        for product in self.pool.get('product.product').browse(cr, uid, cat_products_ids, context):
            if (product.categ_id.magento_rdc_category_default and product.categ_id.magento_rdc_category_default.id == magento_rdc_category_id or
                product.categ_id.magento_omcategory_default_id and product.categ_id.magento_omcategory_default_id.id == magento_omcategory_id):
                product_ids_to_update.append(product.id)

        if product_ids_to_update:
            cr.execute("update product_product set write_date = now() where id in %s", (tuple(product_ids_to_update),))
        return True

    def create(self, cr, uid, vals, context=None):
        category_id = super(ProductCategory, self).create(cr, uid, vals, context)
        if 'magento_rdc_category' in vals or 'magento_omcategory_id' in vals:
            self.write_now_on_category_products(cr, uid, category_id, vals.get('magento_rdc_category'), vals.get('magento_omcategory_id'), context)
        return category_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(ProductCategory, self).write(cr, uid, ids, vals, context)
        if 'magento_rdc_category' in vals or 'magento_omcategory_id' in vals:
            self.write_now_on_category_products(cr, uid, ids, vals.get('magento_rdc_category'), vals.get('magento_omcategory_id'), context)
        return res

ProductCategory()
