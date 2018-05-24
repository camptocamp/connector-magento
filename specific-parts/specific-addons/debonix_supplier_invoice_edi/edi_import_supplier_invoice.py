# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ftplib
import socket
from datetime import datetime, timedelta
from contextlib import contextmanager
from StringIO import StringIO
from openerp.osv import orm, fields, osv
from openerp.tools.translate import _


class EdifactPurchaseInvoiceNotFound(Exception):
    pass


class EdifactPurchaseInvoiceProductNotFound(Exception):
    pass


class EdifactPurchaseInvoiceTotalDifference(Exception):
    pass


class EDIImportSupplierInvoice(orm.AbstractModel):

    _name = 'edi.import.supplier.invoice'

    def cron_import_edi_files(self, cr, uid, context=None):
        """Connect to FTP, retrieve EDI files and update invoices."""
        edi_file_invoices = {}
        with self.ftp_connect(cr, uid, context) as ftp:
            for filename in ftp.nlst():
                if not filename.endswith('.edi'):
                    continue
                data = StringIO()
                ftp.retrbinary('RETR ' + filename, data.write)
                data.seek(0)
                edi_file_invoices[filename] = self.import_edi_file(data)
        self.update_invoices(cr, uid, edi_file_invoices, context=context)

    def _find_invoice(self, cr, uid, purchase_number, context=None):
        """Find the existing invoice from the purchase order number.
        Raise an error if not found or multiple invoices found."""

        company = self._get_company(cr, uid, context=context)
        today_string = fields.date.context_today(self, cr, uid,
                                                 context=context)
        today = datetime.strptime(today_string, '%Y-%m-%d')
        date_approve_limit = (
                today - timedelta(days=company.edifact_supplier_invoice_days)
        ).strftime('%Y-%m-%d')
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_ids = purchase_order_obj.search(cr, uid, [
            ('name', '=', purchase_number),
            ('state', 'in', ('approved', 'except_picking',
                             'except_invoice')),
            ('shipped', '=', True),
            ('date_approve', '>', date_approve_limit),
            ('company_id', '=', company.id)
        ], context=context)
        if not purchase_order_ids:
            raise EdifactPurchaseInvoiceNotFound(
                _('Purchase order not found'))
        purchase_order = purchase_order_obj.browse(
            cr, uid, purchase_order_ids[0], context=context)
        invoices = purchase_order.invoice_ids
        if not invoices:
            raise EdifactPurchaseInvoiceNotFound(
                _('No invoice found for the purchase order'))
        elif len(invoices) > 1:
            raise EdifactPurchaseInvoiceNotFound(
                _('Multiple invoices found for the same purchase order'))
        return invoices[0]

    def _get_code_products_dict(self, cr, uid, invoice, edi_values,
                                context=None):
        """Return a dict matching product_code from the EDI values with the
        products from the invoice.
        Raise an error if no existing product is found for the product_code
        or if the product is not on the invoice.
        """
        edi_product_codes = [
            l.get('product_code') for l in edi_values.get('lines')]
        product_obj = self.pool['product.product']
        product_ids = product_obj.search(cr, uid, [
            ('default_code', 'in', edi_product_codes)], context=context)
        products = product_obj.read(cr, uid, product_ids, ['default_code'],
                                    context=context)
        edi_products_codes_dict = {p['default_code']: p['id'] for p in
                                   products}
        not_found_product_codes = set(edi_product_codes) - set(
            edi_products_codes_dict.keys())
        if not_found_product_codes:
            raise EdifactPurchaseInvoiceProductNotFound(
                _('EDI products not found in the system'),
                list(not_found_product_codes)
            )
        invoice_product_ids = [l.product_id.id for l in invoice.invoice_line]
        not_found_products = set(edi_products_codes_dict.values()) - set(
            invoice_product_ids)
        if not_found_products:
            raise EdifactPurchaseInvoiceProductNotFound(
                _('EDI products not found on the invoice'),
                not_found_products
            )
        return edi_products_codes_dict

    def _prepare_new_invoice_lines(self, cr, uid, invoice, edi_lines,
                                   edi_products_codes_dict, context=None):
        """Prepare invoice line to create according to EDI lines"""
        invoice_line_vals = []
        for edi_line in edi_lines:
            product_id = edi_products_codes_dict.get(
                edi_line.get('product_code'))
            product = self.pool['product.product'].browse(cr, uid, product_id,
                                                          context=context)
            account = product.property_account_expense or \
                product.categ_id.property_account_expense_categ
            if not account:
                raise osv.except_osv(
                    _('Error!'),
                    _('Define expense account for this product: '
                      '"%s" (id:%d).') % (product.name, product.id,))

            supplier_taxes = product.supplier_taxes_id
            # TODO Check because I'm not sure about this one
            # TODO ? Define taxes and fiscal position on the test partner ?
            fiscal_position = invoice.fiscal_position or \
                invoice.partner_id.property_account_position
            taxes_ids = self.pool['account.fiscal.position'].map_tax(
                cr, uid, fiscal_position, supplier_taxes, context=context)
            vals = {
                'name': product.description,
                'product_id': product.id,
                'quantity': edi_line.get('quantity'),
                'price_unit': edi_line.get('price_unit'),
                'account_id': account.id,
                'uos_id': product.uos_id.id,
                'invoice_line_tax_id': [(6, 0, taxes_ids)],
                'edi_line_amount': edi_line.get('line_amount')
            }
            invoice_line_vals.append(vals)
        return invoice_line_vals

    def update_invoices(self, cr, uid, edi_file_invoice_dict, context=None):
        """Update existing invoices with new lines from the EDI files dict.
        Raise an error if something unexpected happens."""
        invoice_obj = self.pool['account.invoice']
        invoice_line_obj = self.pool['account.invoice.line']
        created_invoices = []
        for filename, edi_invoices in edi_file_invoice_dict.iteritems():
            for edi_invoice_values in edi_invoices:

                invoice = self._find_invoice(cr, uid, edi_invoice_values.get(
                    'purchase_number'), context=context)
                invoice_obj.write(cr, uid, invoice.id, {
                    'supplier_invoice_number': edi_invoice_values.get(
                        'supplier_invoice_number'),
                    'date_invoice': edi_invoice_values.get('date_invoice'),
                    'date_due': edi_invoice_values.get('date_due'),
                })

                edi_products_codes_dict = self._get_code_products_dict(
                    cr, uid, invoice, edi_invoice_values, context=context)

                invoice_line_ids = [il.id for il in invoice.invoice_line]
                invoice_obj.unlink(cr, uid, invoice_line_ids, context=context)

                invoice_lines_vals = self._prepare_new_invoice_lines(
                    cr, uid, invoice, edi_invoice_values.get('lines'),
                    edi_products_codes_dict, context=context)

                changed_invoice_lines_vals = []
                # Call product onchange
                for invoice_line_vals in invoice_lines_vals:
                    changed_vals = invoice_line_obj.product_id_change(
                        cr, uid, [], invoice_line_vals.get('product_id'),
                        invoice_line_vals.get('uos_id'),
                        qty=invoice_line_vals.get('quantity'),
                        type=invoice.type,
                        partner_id=invoice.partner_id.id,
                        fposition_id=invoice.fiscal_position.id,
                        price_unit=invoice_line_vals.get('price_unit'),
                        currency_id=invoice.currency_id.id,
                        context=context, company_id=invoice.company_id.id
                    ).get('value')
                    changed_invoice_lines_vals.append(changed_vals)

                invoice_obj.write(cr, uid, invoice.id, {
                    'invoice_line': [
                        (0, False, vals) for vals in changed_invoice_lines_vals
                    ],
                }, context=context)

                # Check totals
                # As we can't match the newly created invoice line with the
                # values coming from the EDI, we'll sum subtotals for each
                # products
                invoice_subtotals = {}
                for invoice_line in invoice.invoice_line:
                    default_code = invoice_line.product_id.default_code
                    if default_code in invoice_subtotals.keys():
                        invoice_subtotals[
                            default_code] += invoice_line.price_subtotal
                    else:
                        invoice_subtotals[
                            default_code] = invoice_line.price_subtotal
                edi_subtotals = {}
                for edi_line in edi_invoice_values.get('lines'):
                    default_code = edi_line.get('product_code')
                    if default_code in edi_subtotals:
                        edi_subtotals[default_code] += edi_line.get(
                            'line_amount')
                    else:
                        edi_subtotals[default_code] = edi_line.get(
                            'line_amount')
                if invoice_subtotals != edi_subtotals:
                    subtotals_dict = self._get_subtotals_differences(
                        invoice_subtotals, edi_subtotals)
                    allowed_difference = self._get_company(
                        cr, uid, context=context
                    ).edifact_supplier_invoice_amount_difference
                    diff_product_codes = {}
                    for code, difference in subtotals_dict.iteritems():
                        if difference > allowed_difference:
                            diff_product_codes[code] = difference
                    if diff_product_codes:
                        raise EdifactPurchaseInvoiceTotalDifference(_(
                            'Different subtotals between the imported EDI and '
                            'updated invoice for these product codes',
                            diff_product_codes
                        ))
                invoice_obj.invoice_validate(cr, uid, [invoice.id],
                                             context=context)
                created_invoices.append(invoice)
        return created_invoices

    def import_edi_file(self, data):
        """Parse the EDI file and return a dict with invoices values."""
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
        company = self._get_company(cr, uid, context=context)
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

    def _get_company(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        return user.company_id

    def _get_subtotals_differences(self, dict1, dict2):
        """Return a dict with absolute value difference for each key in dicts.
        """
        new_dict = {}
        for key, value in dict1:
            new_dict[key] = value
            if dict2.get(key):
                new_dict[key] = abs(new_dict[key] - dict2.get(key))
        for key, value in dict2:
            if key in new_dict.keys():
                continue
            new_dict[key] = value
        return new_dict
