# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright Camptocamp SA
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

from osv import fields, osv, orm
from tools import ustr
from tools.translate import _

import base64
import csv
import tools
from collections import defaultdict
import os
import tempfile



class c2c_sync_product(osv.osv_memory):
    """Sync product"""
    _name = 'c2c.sync.product'
    _description = 'Sync Product'
    _columns = {
        'data': fields.binary('File', required=True),
        'name': fields.char('Filename', 256, required=False),
        'location_id' : fields.many2one('stock.location', 'Location', required=True ,help="Set the location for the inventory and stock level.")
    }


    def action_import(self, cr, uid, ids, context=None):
        """
        Update Price for given Product from the CSV and xls file.
        """
        res = {}
        imported_prod_ids = []
        prod_obj = self.pool.get('product.product')
        model_obj  = self.pool.get('ir.model.data')
        for wiz in self.browse(cr, uid, ids, context):
            if not wiz.data:
                raise osv.except_osv(_('UserError'), _("You need to select a file!"))
            # Decode the file data
            data = wiz.data
            name = wiz.name
            location_id = wiz.location_id
            #(Product type: Stockable, Procurement: MTO, Procurement method: Buy, Unit: PCE, TVA: 19,6%,)
            supp_tax_id = self.pool.get('account.tax').search(cr,uid,[('description','like','05'),('type_tax_use','=','purchase')])
            tax_id = self.pool.get('account.tax').search(cr,uid,[('description','like','01'),('type_tax_use','=','sale')])
            default_dict={
                'type':'product',
                'procure_method':'make_to_order',
                'supply_method':'buy',
                'uom_id':self.pool.get('product.uom').search(cr,uid,[('name','=','PCE')])[0] or False,
                'taxes_id': tax_id and [(6,0,tax_id)] or False,
                'supplier_taxes_id': supp_tax_id and [(6,0,supp_tax_id)] or False,
                'set':self.pool.get('magerp.product_attribute_set').search(cr,uid,[('attribute_set_name','=','Default')])[0] or False,
            }
            dict_products = prod_obj.csvfile_to_dict(cr,uid,data,name)
            imported_prod_ids = prod_obj.import_product_from_dict(cr,uid,dict_products,location_id,default_dict)
            model_data_ids = model_obj.search(cr, uid, [
                            ('model','=','ir.ui.view'),
                            ('module','=','product'),
                            ('name','=','product_normal_form_view')
                        ])
            resource_id = model_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
            res =  {
                    'name': _("Imported Product"),
                    'type': 'ir.actions.act_window',
                    'res_model': 'product.product',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(False,'tree'), (resource_id,'form')],
                    'domain': "[('id', 'in', %s)]" % imported_prod_ids,
                    'context': context,
                }
        return res


c2c_sync_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
