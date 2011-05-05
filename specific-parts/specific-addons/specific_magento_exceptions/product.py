# -*- encoding: utf-8 -*-
# -*- encoding: utf-8 -*-
#########################################################################
#This module intergrates Open ERP with the magento core                 #
#Core settings are stored here                                          #
#########################################################################
#                                                                       #
# Copyright (C) 2009  Sharoon Thomas, Raphaël Valyi                     #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

from osv import osv, fields
import datetime
import base64
import time
from magentoerpconnect import magerp_osv
from tools.translate import _
import netsvc

class product_product(magerp_osv.magerp_osv):
    _inherit = "product.product"


    def export_inventory(self, cr, uid, ids, shop, ctx):
        logger = netsvc.Logger()
        stock_id = self.pool.get('sale.shop').browse(cr, uid, ctx['shop_id']).warehouse_id.lot_stock_id.id
        success_counter = 0
        exception_products = {}
        for product in self.browse(cr, uid, ids):
            if product.magento_exportable and product.magento_sku and product.type != 'service':
                # Changing Stock Availability to "Out of Stock" in Magento
                # if a product has qty lt or equal to 0.
                # And CHANGE the reference quantity to export to Magento
                # For Debonix, we'll use bom_stock value computed into c2c_bom_stock
                try:
                    stock_options = {}
                    if product.magento_manage_stock:
                        bom_stock = self.read(cr, uid, product.id, ['bom_stock'], {'location': stock_id})['bom_stock']
                        stock_options = {
                            'qty': bom_stock,
                            'is_in_stock': True,
                            'use_config_manage_stock': True,
                            'manage_stock': True,
                            'backorders': product.magento_backorders,
                            'use_config_min_sale_qty': True,
                            'use_config_max_sale_qty': True,
                        }
                        notify_msg = "Successfully updated stock level at %s for product with SKU %s " % (bom_stock, product.magento_sku)
                    else:
                        stock_options = {
                            'manage_stock': False,
                            'use_config_manage_stock': False
                        }
                        notify_msg = "Successfully updated stock configuration to not manage stock for product with SKU %s" % (product.magento_sku,)
                    
                    ctx['conn_obj'].call('product_stock.update', [product.magento_sku, stock_options])
                    logger.notifyChannel('ext synchro', netsvc.LOG_INFO, notify_msg)
                    success_counter += 1
                except Exception, e:
                    exception_products[product.id] = e
#                    request = self.pool.get('res.request')
#                    summary = """Error during stock levels update :
#Product code : %s
#Product name %s
#Exception :
#%s""" % (product.default_code, product.name, e)
#                    request.create(cr, uid,
#                                   {'name': "Update stock levels error",
#                                    'act_from': uid,
#                                    'act_to': uid,
#                                    'body': summary,
#                                    })
#                    cr.commit()
#                    raise e
#        return True

        return {'exported_count': success_counter,
                'exception_products': exception_products}

product_product()