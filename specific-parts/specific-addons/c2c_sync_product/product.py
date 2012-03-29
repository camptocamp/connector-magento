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


import cStringIO
import time
import base64
import csv


from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from tools.translate import _

class ProductProduct(Model):
    _inherit = "product.product"
  
    def _convert_to_type(self, chain, to_type):
        """Convert string to to_type param"""
        ret = chain[:]
        if len(ret.strip()) == 0:
            ret = 0
        try:
            ret = to_type(ret)
        except ValueError:
            raise except_osv(_("Error during import"),
                             _("Value \"%s\" cannot be converted to %s.") % (ret, to_type.__name__))
        return ret
        
    def csvfile_to_dict(self,cr,uid,data,name):
        """Return a dict of value read from CSV, converted in the good type."""
        if not data:
            raise except_osv(_('UserError'), _("You need to select a file!"))
        # Decode the file data
        data = base64.b64decode(data)
        input=cStringIO.StringIO(data)
        input.seek(0)
        reader_info = []
        dialect = csv.Sniffer().sniff(input.read(1024))
        input.seek(0)
        reader = csv.reader(input,dialect)
        reader_info.extend(reader)
        origin_header = reader_info[0]
        del reader_info[0]
        # header of the csv
        keys= ['EAN13', 'Company Code', 'Name','Magento SKU','Category', 'Sale Price', 'Export To Magento', 'Standard Price', 'Cost Method',
               'Supplier Code', 'Supplier Delay', 'Supplier Min. Qty','Supplier Product Code', 'Supplier Product Name', 'Quantity', 'Price',
               'Stock Level']
        
        values= {}
        if len(origin_header) <> len(keys):
            raise except_osv(_('UserError'),
                             _("Your file hasn't the right number of column (%s VS %s) ! Expected %s, found %s") %
                               (len(keys), len(origin_header), keys,origin_header))
        res = []
        for i in range(len(reader_info)):
            field = reader_info[i]

            values = dict(zip(keys, field))
            # fields to convert from str to another type
            to_convert = [['Supplier Delay', int],
                          ['Supplier Min. Qty', float],
                          ['Quantity', float],
                          ['Price', float],
                          ['Standard Price', float],
                          ['Sale Price', float],
                          ['Stock Level', int],
                          ['Export To Magento', bool]]
            for item in to_convert:
                values[item[0]] = self._convert_to_type(values[item[0]], item[1])
            res.append(values)
        return res
    
    def _update_supplier_infos(self, cr, uid, product_id, values, prices_not_to_delete):
        """
        Suppliers update. Create or modify suppliers. Delete all lines of prices for a supplier and import new prices
        Args: 
            product ID, 
            values (dict of values for each field, like : {'Supplier Code' : XXX, 'Supplier Delay' : YYY,...})
            prices_not_to_delete (array of ids that don't have to be deleted)
        return dict of ids of supplier infos not to delete
        """
        prod_supplier_obj = self.pool.get('product.supplierinfo')
        pricelist_obj = self.pool.get('pricelist.partnerinfo')
        res_obj = self.pool.get('res.partner')
        prod_supplier_ids = prod_supplier_obj.search(cr, uid, [('product_id', '=', product_id), ('name.ref', '=', values['Supplier Code'])])
        if prod_supplier_ids:
            for prod_supplier in prod_supplier_obj.browse(cr, uid, prod_supplier_ids):
                prod_supplier_obj.write(cr, uid, prod_supplier.id, {'delay': values['Supplier Delay'],
                                                                    'qty': values['Supplier Min. Qty'],
                                                                    'product_code': values['Supplier Product Code'],
                                                                    'product_name': values['Supplier Product Name']})

                if values['Quantity'] > 0 and values['Price'] > 0:
                    if prod_supplier.pricelist_ids:
                        # delete prices lines (only when the first new line of the supplier is found to not delete prices at each line of the csv)
                        if (product_id, prod_supplier.id) not in prices_not_to_delete:
                            # delete price lines
                            price_ids = pricelist_obj.search(cr, uid, [('suppinfo_id','=', prod_supplier.id)])
                            pricelist_obj.unlink(cr, uid, price_ids)
                            prices_not_to_delete.append((product_id, prod_supplier.id))

                    pricelist_obj.create(cr, uid,
                                         {'min_quantity': values['Quantity'],
                                          'price': values['Price'],
                                          'suppinfo_id': prod_supplier.id})

        else:
            partner_ids = res_obj.name_search(cr, uid, values['Supplier Code'],
                                              args=[('supplier', '=', True)],
                                              operator='ilike', context=None, limit=80)
            if not partner_ids:
                raise except_osv(_('Error'),
                                 _('The supplier code %s has not been found'
                                   '(verify it is define as a supplier with the checkbox ticked)!') %
                                   (values['Supplier Code']))
            new_supplier_ids = prod_supplier_obj.create(cr, uid ,
                    {'name':  partner_ids[0][0],
                     'delay': values['Supplier Delay'],
                     'qty':values['Supplier Min. Qty'],
                     'product_id':product_id,
                     'product_code': values['Supplier Product Code'],
                     'product_name': values['Supplier Product Name']
                     })
            pricelist_obj.create(cr, uid, {'min_quantity': values['Quantity'],
                                           'price': values['Price'],
                                           'suppinfo_id': new_supplier_ids})
            prices_not_to_delete.append((product_id, new_supplier_ids))

        return prices_not_to_delete
    
    def _build_product_dict(self,cr,uid,values,default_dict={}):
        """
        Build the dict to create or update product (convert name of csv column to object field)
        """                   
        product_data = {}
    
        # Simple one
        if values['EAN13'].strip() != '':
            product_data.update({'ean13': values['EAN13']})
        if values['Name'].strip() != '':
            product_data.update({'name': values['Name']})
        if values['Magento SKU'].strip() != '':
            product_data.update({'magento_sku': values['Magento SKU']})
        if values['Sale Price'] != 0:
            product_data.update({'list_price': values['Sale Price']})
        if values['Standard Price'] != 0:
            product_data.update({'standard_price': values['Standard Price']})
        if values['Cost Method'].strip() != '' :
            product_data.update({'cost_method': values['Cost Method']})
        if values['Company Code'].strip() != '' :
            product_data.update({'default_code': values['Company Code']})

        if values['Category'].strip() != '' :
            cat_id=self.pool.get('product.category').search(cr, uid, [('name', '=', values['Category'])])[0]
            if not cat_id:
                raise except_osv(_('Error'),
                                 _('The category %s has not been found !') % (values['Category']))
            product_data.update({'categ_id': cat_id})
        
        # May be something wrong if not using "False" and "True" in the file
        product_data.update({'magento_exportable': values['Export To Magento']})

        # Add default one
        product_data.update(default_dict)
        
        return product_data
    
    def import_product_from_dict(self,cr,uid,products_dict,location_id,default_dict={}):
        """Create or update the product according to dict issue from csvfile_to_dict.
           Return ids of updated/created products.Create an inventory for the given location 
           and confirm it with given value for each product"""
        
        imported_prod_ids = []
        prices_not_to_delete = []
        prod_obj = self.pool.get('product.product')
        inv_line_obj = self.pool.get('stock.inventory.line')
        inv_obj = self.pool.get('stock.inventory')
        inventory_id = inv_obj.create(cr, uid, {'name':'SYNC INVENTORY '+time.strftime('%Y-%m-%d %H:%M:%S')})
        
        for values in products_dict:
            prod_ids = prod_obj.search(cr, uid, [('default_code', '=' ,values['Company Code'])])
            if len(prod_ids) > 1:
                raise except_osv(_('Error'),
                                 _('More than one product has the code %s !') % (values['Company Code']))
            product_data = self._build_product_dict(cr, uid, values, default_dict)
            if prod_ids:
                prod_id=prod_ids[0]
                prod = prod_obj.browse(cr, uid, prod_id)
                if values['Supplier Code'] != '':
                    prices_not_to_delete = self._update_supplier_infos(cr, uid, prod.id,
                                                                       values, prices_not_to_delete)
                prod_obj.write(cr, uid, prod.id, product_data)
                imported_prod_ids.append(prod_id)
            else:
                prod_id = prod_obj.create(cr,uid,product_data)
                prices_not_to_delete = self._update_supplier_infos(cr,uid,prod_id,values,prices_not_to_delete)
                imported_prod_ids.append(prod_id)
            if imported_prod_ids.count(prod_id) == 1:
                inv_line_obj.create(cr,uid,{
                        'inventory_id' : inventory_id,
                        'location_id' : location_id.id,
                        'product_id' : imported_prod_ids[-1],
                        'product_uom' : default_dict['uom_id'],
                        'product_qty' : values['Stock Level'],
                    })
        inv_obj.action_done(cr,uid,[inventory_id])
        imported_prod_ids=list(set(imported_prod_ids))
        return imported_prod_ids
