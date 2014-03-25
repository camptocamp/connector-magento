# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Camptocamp
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

import cStringIO
import base64
import tempfile
import csv

from openerp.osv.orm import TransientModel, fields
from openerp.osv.osv import except_osv
from tools.translate import _



class PriceListImporter(TransientModel):
    """Import Pricelist"""
    _name = 'c2c.import.pricelist'
    _description = 'Import Pricelist'
    _columns = {
        'data': fields.binary('File', required=True),
        'name': fields.char('Filename', 256, required=False),
    }

    def _convert_to_type(self, chain, to_type):
        """Convert string to to_type param"""
        ret = chain[:]
        if len(ret.strip()) == 0:
            ret = 0
        try:
            ret = to_type(ret)
        except ValueError:
            raise except_osv(_("Error during pricelist import"),
                             _("Value \"%s\" cannot be converted to %s.")  % (ret, to_type.__name__))
        return ret

    def action_import(self, cr, uid, ids, context=None):
        """
        Update Price for given Product from the CSV and xls file.
        """
        res = {}
        imported_prod_ids = []
        prod_obj = self.pool.get('product.product')
        prod_supplier_obj = self.pool.get('product.supplierinfo')
        pricelist_obj = self.pool.get('pricelist.partnerinfo')
        model_obj  = self.pool.get('ir.model.data')
        res_obj = self.pool.get('res.partner')

        for wiz in self.browse(cr, uid, ids, context):
            if not wiz.data:
                raise except_osv(_('UserError'),
                                 _("You need to select a file!"))
            # Decode the file data
            data = base64.b64decode(wiz.data)
            file_type = (wiz.name).split('.')
            input = cStringIO.StringIO(data)
            #seek is deprecated
            input.seek(0)
            reader_info = []
            if file_type[1] == 'xls':
                try:
                    import xlrd
                except ImportError:
                    print "xlrd python lib  not installed"

                if xlrd:
                    file_1 = base64.decodestring(wiz.data)
                    # Watch out file is never deleted we should use TemporaryFile instead
                    (fileno, fp_name) = tempfile.mkstemp('.xls', 'openerp_')
                    file = open(fp_name, "w")
                    file.write(file_1)
                    file.close()
                    #Read xls file.
                    book = xlrd.open_workbook(fp_name)
                    sheet = book.sheet_by_index(0)
                    for counter in range(sheet.nrows-1): # Loop for number of rows
                    # grab the current row
                        rowValues = sheet.row_values(counter+1,0, end_colx=sheet.ncols)
                        row =map(lambda x: str(x), rowValues)
                        reader_info.append(row)

            if file_type[1] == 'csv':
                # we should use dict reader instead
                reader = csv.reader(input, delimiter=';', lineterminator='\r\n')
                reader_info.extend(reader)
                del reader_info[0]

            keys = []
            values= {}
            # header of the csv
            # bad way to do it beacause odrer has now importance
            # key should be extracted from frist row and validated
            keys= ['id', 'EAN13', 'Company Code', 'Supplier Code', 'Supplier Delay',
                   'Supplier Min. Qty', 'Supplier Product Code', 'Supplier Product Name', 'Quantity', 'Price']

            prices_not_to_delete = []

            for i in range(len(reader_info)):
                field = reader_info[i]
                # bad design we can not ensure that col and name match
                values = dict(zip(keys, field))

                if file_type[1] == 'csv':
                    # fields to convert from str to another type
                    to_convert = [['id', int],
                                  ['Supplier Delay', int],
                                  ['Supplier Min. Qty', float],
                                  ['Quantity', float],
                                  ['Price', float]]
                    for item in to_convert:
                        values[item[0]] = self._convert_to_type(values[item[0]], item[1])

                prod_ids = values['id']

                if prod_ids:
                    updated = False
                    for prod in prod_obj.browse(cr, uid, [prod_ids]):
                        """
                        Suppliers update. Create or modify suppliers. Delete all lines of prices for a supplier and import new prices
                        """
                        if values['Supplier Code'] != '':
                            prod_supplier_ids = prod_supplier_obj.search(cr, uid, [('product_id','=', prod.id),
                                                                                   ('name.ref', '=', values['Supplier Code'])])
                            if prod_supplier_ids:
                                for prod_supplier in prod_supplier_obj.browse(cr, uid, prod_supplier_ids):
                                    prod_supplier_obj.write(cr, uid, prod_supplier.id, {'delay': values['Supplier Delay'],
                                                                                        'min_qty': values['Supplier Min. Qty'],
                                                                                        'product_code': values['Supplier Product Code'],
                                                                                        'product_name': values['Supplier Product Name']})

                                    if values['Quantity'] > 0 and values['Price'] > 0:
                                        if prod_supplier.pricelist_ids:
                                            # delete prices lines (only when the first new line of the supplier is found to not delete prices at each line of the csv)
                                            if (prod.id, prod_supplier.id) not in prices_not_to_delete:
                                                # delete price lines
                                                price_ids = pricelist_obj.search(cr, uid, [('suppinfo_id','=', prod_supplier.id)])
                                                pricelist_obj.unlink(cr, uid, price_ids)
                                                prices_not_to_delete.append((prod.id, prod_supplier.id))

                                        pricelist_obj.create(cr, uid,
                                                             {'min_quantity': values['Quantity'],
                                                              'price': values['Price'],
                                                              'suppinfo_id': prod_supplier.id})

                            else:
                                partner_ids = res_obj.name_search(cr, uid, values['Supplier Code'],
                                                                  args=[('supplier', '=', True)],
                                                                  operator='ilike', context=None, limit=80)
                                new_supplier_ids = prod_supplier_obj.create(cr, uid ,
                                        {'name':  partner_ids[0][0],
                                         'delay': values['Supplier Delay'],
                                         'qty':values['Supplier Min. Qty'],
                                         'product_id':prod.id,
                                         'product_code': values['Supplier Product Code'],
                                         'product_name': values['Supplier Product Name']})

                                pricelist_obj.create(cr, uid, {'min_quantity': values['Quantity'],
                                                               'price': values['Price'],
                                                               'suppinfo_id': new_supplier_ids})
                                prices_not_to_delete.append((prod.id, new_supplier_ids))
                            updated = True

                        """
                        Product update. Modify the ean13 or default_code
                        """
                        product_data = {}
                        if values['EAN13'].strip() != '' and prod.ean13 != values['EAN13']:
                            product_data.update({'ean13': values['EAN13']})
                        if values['Company Code'].strip() != '' and prod.default_code != values['Company Code']:
                            product_data.update({'default_code': values['Company Code']})

                        if len(product_data) > 0:
                            prod_obj.write(cr, uid, prod.id, product_data)
                            updated = True

                        if updated:
                            imported_prod_ids.append(prod.id)

                    model_data_ids = model_obj.search(cr, uid, [('model','=','ir.ui.view'),
                                                                ('module','=','product'),
                                                                ('name','=','product_normal_form_view')])
                    resource_id = model_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']

                res =  {'name': _("Imported Product"),
                        'type': 'ir.actions.act_window',
                        'res_model': 'product.product',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'views': [(False,'tree'), (resource_id,'form')],
                        'domain': "[('id', 'in', %s)]" % imported_prod_ids,
                        'context': context}
        return res
