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
        with self.ftp_connect(cr, uid, context) as ftp:
            for filename in ftp.nlst():
                if not filename.endswith('.edi'):
                    continue
                data = StringIO()
                ftp.retrbinary('RETR ' + filename, data.write)
                self.import_edi_file(data)

    def import_edi_file(self, cr, uid, data, context=None):
        pass

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
