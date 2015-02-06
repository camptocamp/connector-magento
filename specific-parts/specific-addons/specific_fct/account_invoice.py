# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from StringIO import StringIO
import paramiko
from openerp.osv import orm, fields
from openerp import netsvc
import logging
import socket

logger = logging.getLogger(__name__)


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'invoice_to_send': fields.boolean("Invoice to send to Magento"),
    }

    _defaults = {
        'invoice_to_send': False,
    }

    def ftp_invoice(self, cr, uid, invoice, context=None):
        # move the invoice to a sftp folder if it is a Magento
        # invoice
        data_obj = self.pool['ir.model.data']
        report_obj = self.pool['ir.actions.report.xml']
        mail_group_obj = self.pool['mail.group']

        sale = invoice.sale_ids[0]
        if not sale.magento_bind_ids:
            return True

        user_obj = self.pool['res.users']
        user = user_obj.browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.sftp_invoice_host or not company.sftp_invoice_port:
            return True

        __, report_id = data_obj.get_object_reference(
            cr, uid, 'account', 'account_invoices')
        report = report_obj.browse(cr, uid, report_id, context=context)
        report_service = 'report.%s' % report.report_name
        service = netsvc.LocalService(report_service)
        result, ext = service.create(cr, uid, [invoice.id],
                                     {'model': 'account.invoice'},
                                     context=context)
        content = StringIO(result)
        filename = "%s-%s.%s" % (sale.name, invoice.number, ext)
        try:
            transport = paramiko.Transport((company.sftp_invoice_host,
                                            company.sftp_invoice_port))
            try:
                transport.connect(username=company.sftp_invoice_user,
                                  password=company.sftp_invoice_password)
                client = paramiko.SFTPClient.from_transport(transport)
                try:
                    client.chdir(company.sftp_invoice_path)
                    client.putfo(content, filename)
                    # write as sent, in case it is a retry
                    invoice.write({'invoice_to_send': False})
                finally:
                    client.close()
            finally:
                transport.close()
        except (paramiko.SSHException, socket.error) as err:
            # No connection available: put it as to be retried by cron
            invoice.write({'invoice_to_send': True})
            message = "Exception connection to SFTP server " \
                      "%s on port %s : %s" % (company.sftp_invoice_host,
                                              company.sftp_invoice_port,
                                              str(err))
            logger.warn(message)
            __, mail_group_id = data_obj.get_object_reference(
                cr, uid, 'specific_fct', 'group_sftp_invoice')
            mail_group_obj.message_post(
                cr, uid, [mail_group_id],
                body=message,
                subtype='mail.mt_comment',
                context=context)
            return False
        return True

    def send_invoice(self, cr, uid, ids, context=None):
        data_obj = self.pool['ir.model.data']
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.type != 'out_invoice':
                continue
            if not invoice.sale_order_ids:
                return
            email_obj = self.pool['email.template']
            __, template_id = data_obj.get_object_reference(
                cr, uid, 'account', 'email_template_edi_invoice')
            email_obj.send_mail(cr, uid, template_id, invoice.id)
            invoice.write({'sent': True})

            # Keep iterating even if report is not sent on SFTP.
            self.ftp_invoice(cr, uid, invoice, context=context)
        return True

    def retry_invoices_to_send(self, cr, uid, ids=None,
                               domain=None, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if ids is None:
            if domain is None:
                domain = [('invoice_to_send', '=', True)]
            ids = self.search(cr, uid, domain, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            passed = self.ftp_invoice(cr, uid, invoice, context=context)
            if not passed:
                # ftp_invoice() returned False, stop the cron after first
                # message due to issues with connection.
                break
            # Commit if passed, in order to avoid losing already-sent invoices
            # in case of non-SSHException.
            cr.commit()
        return True
