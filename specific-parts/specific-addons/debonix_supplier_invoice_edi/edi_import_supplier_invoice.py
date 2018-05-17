# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ftplib
import socket
from contextlib import contextmanager
from StringIO import StringIO
from openerp.osv import orm


class EDIImportSupplierInvoice(orm.AbstractModel):

    _name = 'edi.import.supplier.invoice'

    def cron_import_edi_files(self, cr, uid, context=None):
        invoice_values = []
        with self.ftp_connect(cr, uid, context) as ftp:
            for filename in ftp.nlst():
                if not filename.endswith('.edi'):
                    continue
                data = StringIO()
                ftp.retrbinary('RETR ' + filename, data.write)
                data.seek(0)
                invoice_values += self.import_edi_file(data)
        self.create_invoices(cr, uid, invoice_values, context=context)

    def create_invoices(self, cr, uid, invoice_values, context=None):
        # TODO in BSDEB-4
        pass

    def import_edi_file(self, data):
        invoice_values = []
        temp_invoice_values = {}
        temp_invoice_line_values = []
        for line in data.readlines():
            if line.startswith('100'):
                supplier_invoice_number = line[3:38].rstrip()
                edi_raw_invoice_type = line[46:47]
                if edi_raw_invoice_type == 'F':
                    invoice_type = 'out_invoice'
                elif edi_raw_invoice_type == 'A':
                    invoice_type = 'out_refund'
                date_invoice = line[48:56]
                date_due = line[78:86]
                temp_invoice_values.update({
                    'supplier_invoice_number': supplier_invoice_number,
                    'invoice_type': invoice_type,
                    'date_invoice': date_invoice,
                    'date_due': date_due
                })
            if line.startswith('200'):
                if not temp_invoice_values.get('purchase_number'):
                    temp_invoice_values.update({
                        'purchase_number': line[38:73].rstrip()
                    })
                quantity = float(line[335:350].lstrip('0')) / 1000
                line_amount = float(line[392:407].lstrip('0')) / 10000
                price_unit = float(line[407:422].lstrip('0')) / 10000
                product_code = line[612:621]
                temp_invoice_line_values.append({
                    'quantity': quantity,
                    'line_amount': line_amount,
                    'price_unit': price_unit,
                    'product_code': product_code
                })
            if line.startswith('FIN'):
                temp_invoice_values.update({
                    'lines': temp_invoice_line_values
                })
                invoice_values.append(temp_invoice_values)

                temp_invoice_values = {}
                temp_invoice_line_values = []
        return invoice_values

    @contextmanager
    def ftp_connect(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        ftp_host = company.edifact_host
        ftp_user = company.edifact_user
        ftp_pw = company.edifact_password
        ftp_import_path = company.edifact_supplier_invoice_import_path
        ftp = False
        try:
            # Connect to FTP
            ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pw)
            ftp.cwd(ftp_import_path)
            yield ftp
        except (socket.error, ftplib.Error) as err:
            raise UserWarning("Could not connect to FTP : %s" % err.message)
        finally:
            if ftp:
                ftp.close()
