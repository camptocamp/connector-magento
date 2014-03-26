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
import StringIO
import base64
import csv

from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp import pooler
from openerp import tools

try:
    import xlwt
    excel_enabled = True
except ImportError:
    print 'xlwt Python module not installed'
    excel_enabled = False


# if excel_enabled:
    # class XlsDoc(xl.CompoundDoc.XlsDoc):
    #     def saveAsStream(self, ostream, stream):
    #         # 1. Align stream on 0x1000 boundary (and therefore on sector boundary)
    #         padding = '\x00' * (0x1000 - (len(stream) % 0x1000))
    #         self.book_stream_len = len(stream) + len(padding)

    #         self.__build_directory()
    #         self.__build_sat()
    #         self.__build_header()

    #         ostream.write(self.header)
    #         ostream.write(self.packed_MSAT_1st)
    #         ostream.write(stream)
    #         ostream.write(padding)
    #         ostream.write(self.packed_MSAT_2nd)
    #         ostream.write(self.packed_SAT)
    #         ostream.write(self.dir_stream)

    # class Workbook(xl.Workbook):
    #     def save(self, stream):
    #         doc = XlsDoc()
    #         doc.saveAsStream(stream, self.get_biff_data())    


class PriceListExporter(orm.TransientModel):
    """Export Pricelist"""
    _name = 'product.pricelist.export'
    _description = 'Export Pricelist'
    _columns = {
        'data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', readonly=True),
        'format': fields.selection(
            [('xls', 'XLS'),
             ('csv', 'CSV')
             ],
            'Save As:'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('done', 'Done')],
                                  string='State'),
    }

    _defaults = {
        'format': 'csv',
        'state': 'draft',
    }

    def export_data(self, cr, uid, ids, context=None):
        product_obj = self.pool['product.product']
        assert len(ids) == 1
        wiz = self.browse(cr, uid, ids, context=context)[0]
        if wiz.format == 'xls':
            if not excel_enabled:
                raise orm.except_orm(
                    _("Export Pricelist error"),
                    _("Impossible to export the pricelist as an Excel file."
                      "Please install xlwt to enable this feature."))

            filename = 'PriceList.xls'
        else:
            filename = 'PriceList.csv'

        if wiz.format == 'xls':
            mydoc = xlwt.Workbook()
            # Add a worksheet
            mysheet = mydoc.add_sheet("Pricelist")
            # write headers
            header_font = xlwt.Font() # make a font object
            header_font.bold = True
            # font needs to be style actually
            header_style = xlwt.XFStyle()
            header_style.font = header_font

        keys = ['', '']
        file_csv = StringIO.StringIO()
        # header of the csv
        keys = ['id', 'EAN13', 'Company Code', 'Supplier Code',
                'Supplier Delay', 'Supplier Min. Qty',
                'Supplier Product Code', 'Supplier Product Name',
                'Quantity', 'Price']
        key_values = [tools.ustr(k).encode('utf-8') for k in keys]

        if wiz.format == 'xls':
            for col, value in enumerate(key_values):
                mysheet.write(0, col, value, header_style)
        else:
            writer = csv.writer(file_csv, delimiter=';', lineterminator='\r\n')
            writer.writerow(keys)

        prod_ids = product_obj.search(cr, uid, [], context=context)
        for prod in product_obj.browse(cr, uid, prod_ids, context=context):
            row_lst = []
            row = []
            row.append(prod.id)
            row.append(prod.ean13 or ' ')
            row.append(prod.default_code or ' ')
            if prod.seller_ids:
                for seller in prod.seller_ids:
                    for supplier in seller.pricelist_ids:
                        row.append(seller.name.ref or '')
                        row.append(seller.delay or ' ')
                        row.append(seller.qty or ' ')
                        row.append(seller.product_name or ' ')
                        row.append(seller.product_code or ' ')
                        row.append(supplier.min_quantity or ' ')
                        row.append(supplier.price or ' ')
                        if wiz.format == 'xls':
                            row_lst.append(row)
                        else:
                            writer.writerow(row)
            else:
                row += [''] * 7
                if wiz.format == 'xls':
                    row_lst.append(row)
                else:
                    writer.writerow(row)

        if wiz.format == 'xls':
            for row_num, row_values in enumerate(row_lst):
                row_num += 1  # start at row 1
                for col, value in enumerate(row_values):
                    # normal row
                    mysheet.write(row_num, col,
                                  tools.ustr(value).encode('utf-8'))
            file_xls = StringIO.StringIO()
            out = mydoc.save(file_xls)
            out = base64.encodestring(file_xls.getvalue())
        else:
            out = base64.encodestring(file_csv.getvalue())
        result = self.write(cr, uid, ids,
                            {'data': out,
                             'name': filename,
                             'state': 'done'},
                            context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }
