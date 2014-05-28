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
from openerp.osv import orm
from openerp import netsvc


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def send_invoice(self, cr, uid, ids, context=None):
        data_obj = self.pool['ir.model.data']
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.type != 'out_invoice':
                continue
            if not invoice.sale_order_ids:
                return
            email_obj = self.pool['email.template']
            __, template_id = data_obj.get_object_reference(
                cr, uid, 'specific_fct', 'email_template_customer_invoice')
            email_obj.send_mail(cr, uid, template_id, invoice.id)

            # move the invoice to a sftp folder if it is a Magento
            # invoice
            sale = invoice.sale_ids[0]
            if not sale.magento_bind_ids:
                continue

            user_obj = self.pool['res.users']
            user = user_obj.browse(cr, uid, uid, context=context)
            company = user.company_id
            if not company.sftp_invoice_host or not company.sftp_invoice_port:
                continue

            report_obj = self.pool['ir.actions.report.xml']
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
            transport = paramiko.Transport((company.sftp_invoice_host,
                                            company.sftp_invoice_port))
            try:
                transport.connect(username=company.sftp_invoice_user,
                                  password=company.sftp_invoice_password)
                client = paramiko.SFTPClient.from_transport(transport)
                try:
                    client.chdir(company.sftp_invoice_path)
                    client.putfo(content, filename)
                finally:
                    client.close()
            finally:
                transport.close()

        return True
