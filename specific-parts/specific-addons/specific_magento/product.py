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

from openerp.addons.connector.unit.mapper import backend_to_m2o
from openerp.addons.magentoerpconnect.product import (
    ProductImport,
    ProductImportMapper,
    )
from .backend import magento_debonix


@magento_debonix
class DebonixProductImport(ProductImport):
    _model_name = ['magento.product.product']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        super(DebonixProductImport, self)._import_dependencies()
        record = self.magento_record
        self._import_dependency(record['marque'],
                                'magento.product.brand')


@magento_debonix
class DebonixProductImportMapper(ProductImportMapper):
    _model_name = 'magento.product.product'

    direct = (ProductImportMapper.direct +
              [(backend_to_m2o('marque', binding='magento.product.brand'),
                'product_brand_id'),
               ])

# ---- BELOW: TO REVIEW ----

# from osv import osv, fields



# class magerp_product_attributes(osv.osv):
#     """ Inherit magerp.product_attributes in order to add attributes to hide
#         from the product screen """
#     _inherit = 'magerp.product_attributes'

#     def __init__(self, pool, cr):
#         """ Add attribute codes in the list of hidden attributes """
#         super(magerp_product_attributes, self).__init__(pool, cr)
#         # attributes which are not synchronized with openerp
#         self._no_create_list.extend([
#                                     'zdbx_default_ean13',
#                                     'zdbx_default_code',
#                                     'zdbx_default_set_pack',
#                                     'zdbx_default_sku_coffrets',
#                                     'fupid',
#                                     'mpid',
#                                     'soldes_qty',
#                                     'cdiscount_sku',
#                                     'destockage_qty',
#                                     'pyksel_rdc_deliverytype',
#                                     'pyksel_rdc_expeditiondelay',
#                                     'pyksel_rdc_expeditiondelay_unit',
#                                     'pyksel_rdc_availability',
#                                     'pyksel_rdc_gender',
#                                     'pyksel_rdc_cancellation',
#                                     'rdc_active',
#                                     ])
#         # attributes which have to be stored
#         # in regular fields
#         self._not_store_in_json.extend([
#             'zdbx_default_marque',
#         ])

# magerp_product_attributes()


# class Product(osv.osv):
#     """ Inherit product for magento customizations"""

#     _inherit = 'product.product'

#     _columns = {
#         'to_deactivate': fields.boolean(
#             'To deactivate',
#             help="If checked, on the next Export catalog, the product will be "
#             "deactivated on Magento and then on OpenERP. If an open picking "
#             "using this product exists on OpenERP, the product will not be "
#             "deactivated before the next Export catalog."),
#         # boolean not used because user input is really mandatory
#         # and for a boolean, no selected value = false => no error
#         # if not filled
#         'magerp_rdc_active': fields.selection(
#             (('no', 'No'), ('yes', 'Yes')),
#             'Autoriser l\'export vers la galerie marchande',
#             required=True)
#     }

#     def try_deactivate_product(self, cr, uid, ids, context):
#         # we have to avoid to deactivate products
#         # used in pickings to not block them
#         product_ids = ids[:]
#         products_not_to_deactivate = []
#         stock_move_obj = self.pool.get('stock.move')
#         # get opened stock moves using a product to deactivate
#         moves = stock_move_obj.search(
#             cr, uid,
#             [('product_id', 'in', ids),
#              ('state', 'not in', ('cancel', 'done'))],
#             context=context)
#         for move in stock_move_obj.browse(cr, uid, moves, context=context):
#             products_not_to_deactivate.append(move.product_id.id)
#         # keep only unique ids
#         products_not_to_deactivate = list(set(products_not_to_deactivate))
#         # remove products used by stock moves from the products to deactivate
#         [product_ids.remove(id) for id in products_not_to_deactivate]
#         self.write(cr, uid, product_ids, {'active': False} , context=context)
#         cr.commit()
#         return True

# Product()


# class ProductCategory(osv.osv):
#     """Modify the available magento sorting options."""
#     _inherit = "product.category"

#     def _recursive_category_ids(self, cr, uid, id, field_names, context=None):
#         """ Return the Rue Du Commerce / Outilmania Categories of the category.
#         Search recursively from the bottom of the tree"""
#         category = self.browse(cr, uid, id, context=context)
#         res = {}
#         if (category.magento_rdc_category and
#             'magento_rdc_category_default' in field_names):
#             res['magento_rdc_category_default'] = \
#                 category.magento_rdc_category.id
#             field_names.remove('magento_rdc_category_default')
#         if (category.magento_omcategory_id and
#             'magento_omcategory_default_id' in field_names):
#             res['magento_omcategory_default_id'] = \
#                 category.magento_omcategory_id.id
#             field_names.remove('magento_omcategory_default_id')

#         if field_names:
#             if category.parent_id:
#                 res.update(self._recursive_category_ids(
#                     cr, uid, category.parent_id.id, field_names, context))
#         return res

#     def _get_magento_category_ids(self, cr, uid, ids, field_name, arg, context):
#         res = {}
#         for id in ids:
#             res_id = dict((field, False) for field in field_name)
#             res_id.update(
#                 self._recursive_category_ids(
#                     cr, uid, id, field_name[:], context))
#             res[id] = res_id
#         return res

#     _columns = {
#         'magento_rdc_category':
#             fields.many2one('magerp.product_attribute_options',
#                             'Rue Du Commerce Category',
#                             domain="[('attribute_id', '=', 268)]",
#                             ondelete="set null",
#                             help="Rue Du Commerce category applied on products"
#                             " of this category."),
#         'magento_omcategory_id':
#             fields.many2one('magerp.product_attribute_options',
#                             'Outilmania category',
#                             domain="[('attribute_id', '=', 302)]",
#                             ondelete="set null",
#                             help="Outilmania category applied on products"
#                             " of this category."),
#         'magento_rdc_category_default':
#             fields.function(_get_magento_category_ids,
#                             type='many2one',
#                             obj='magerp.product_attribute_options',
#                             method=True,
#                             string='Rue Du Commerce Parent Category',
#                             multi='magento_categories'),
#         'magento_omcategory_default_id':
#             fields.function(_get_magento_category_ids,
#                             type='many2one',
#                             obj='magerp.product_attribute_options',
#                             method=True,
#                             string='OutilMania Parent Category',
#                             multi='magento_categories'),
#         }

#     def write_now_on_category_products(self, cr, uid, ids,
#                                        magento_rdc_category_id,
#                                        magento_omcategory_id,
#                                        context=None):
#         """ We have to update the products on Magento. So we put the write_date
#         to now() on products which are in or below the
#          category. To limit the number of products to update, we select only
#          the products of the child categories which have the same
#          Rue du commerce category (so the ones that have been impacted)."""
#         # all the products of the category and childs
#         cat_products_ids = self.pool.get('product.product').search(
#             cr, uid, [('categ_id','child_of',[ids])], context=context)
#         product_ids_to_update = []
#         # We check each product to see wether it use an other rdc category
#         # It's a bit expensive in term of performance but the most products we
#         # can exclude from the export catalog of magento, the
#         # better it is, so we have advantage of loss some time here but gain
#         # in export catalog
#         for product in self.pool.get('product.product').browse(
#             cr, uid, cat_products_ids, context):
#             if (product.categ_id.magento_rdc_category_default and
#                 product.categ_id.magento_rdc_category_default.id ==
#                 magento_rdc_category_id or
#                 product.categ_id.magento_omcategory_default_id and
#                 product.categ_id.magento_omcategory_default_id.id ==
#                 magento_omcategory_id):
#                 product_ids_to_update.append(product.id)

#         if product_ids_to_update:
#             cr.execute("update product_product set write_date = now() "
#                        "where id in %s", (tuple(product_ids_to_update),))
#         return True

#     def create(self, cr, uid, vals, context=None):
#         category_id = super(ProductCategory, self).create(cr, uid, vals, context)
#         if 'magento_rdc_category' in vals or 'magento_omcategory_id' in vals:
#             self.write_now_on_category_products(
#                 cr, uid, category_id,
#                 vals.get('magento_rdc_category'),
#                 vals.get('magento_omcategory_id'),
#                 context)
#         return category_id

#     def write(self, cr, uid, ids, vals, context=None):
#         res = super(ProductCategory, self).write(cr, uid, ids, vals, context)
#         if 'magento_rdc_category' in vals or 'magento_omcategory_id' in vals:
#             self.write_now_on_category_products(
#                 cr, uid, ids,
#                 vals.get('magento_rdc_category'),
#                 vals.get('magento_omcategory_id'),
#                 context)
#         return res

# ProductCategory()
