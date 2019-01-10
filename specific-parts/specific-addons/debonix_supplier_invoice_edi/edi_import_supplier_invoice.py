# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import ftplib
import socket
from datetime import datetime, timedelta
from contextlib import contextmanager
from StringIO import StringIO
from openerp.osv import orm, fields, osv
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc


class EdifactPurchaseInvoiceParsingError(Exception):
    pass


class EdifactPurchaseInvoiceNotFound(Exception):
    pass


class EdifactPurchaseInvoiceProductNotFound(Exception):

    def __init__(self, msg, product_list=None):
        super(EdifactPurchaseInvoiceProductNotFound, self).__init__(msg)
        self.products = product_list

    def __str__(self):
        res = super(EdifactPurchaseInvoiceProductNotFound, self).__str__()
        return '%s : %s' % (res, ', '.join(self.products))


class EdifactPurchaseInvoiceTotalDifference(Exception):

    def __init__(self, msg, lines_list=None):
        super(EdifactPurchaseInvoiceTotalDifference, self).__init__(msg)
        self.lines = lines_list

    def __str__(self):
        res = super(EdifactPurchaseInvoiceTotalDifference, self).__str__()
        lines_texts = []
        for line in self.lines:
            lines_texts.append('(%s : EDI %s - Subtotal %s)' % (
                line.name.replace('\n', ' '),
                line.edi_line_amount,
                line.price_subtotal))
        return '%s : %s' % (res, ', '.join(lines_texts))


class EDIImportSupplierInvoice(orm.AbstractModel):

    _name = 'edi.import.supplier.invoice'

    @contextmanager
    def ftp_connect(self, cr, uid, context=None):
        """Yield an FTP connection according to edifact settings on company."""
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

    def cron_import_edi_files(self, cr, uid, context=None):
        """Connect to FTP, retrieve EDI files and create/update invoices."""
        company = self._get_company(cr, uid, context=context)
        edi_file_invoices = {}
        with self.ftp_connect(cr, uid, context) as ftp:
            for filename in ftp.nlst():
                if not filename.endswith('.edi'):
                    continue
                data = StringIO()
                ftp.retrbinary('RETR ' + filename, data.write)
                data.seek(0)
                edi_file_invoices[filename] = self.parse_edi_file(data)
        results = self.create_or_update_invoices(
            cr, uid, edi_file_invoices, context=context)
        fails = results.get('failing')
        if fails:
            failed_edi_file = self.handle_failures(
                cr, uid, fails, context=context)
        successes = results.get('successful')
        if successes:
            success_edi_file = self.handle_successes(
                cr, uid, successes, context=context)
        with self.ftp_connect(cr, uid, context) as ftp:
            if successes:
                # Write successful chunks
                ftp.cwd(company.edifact_supplier_invoice_import_success_path)
                ftp.storbinary('STOR %s-success.edi' % fields.date.today(),
                               success_edi_file)
            if fails:
                # Write failing chunks
                ftp.cwd(company.edifact_supplier_invoice_import_error_path)
                ftp.storbinary('STOR %s-fail.edi' % fields.date.today(),
                               failed_edi_file)
            # Commit here to ensure we don't delete original files before
            # changes are persisted in DB
            cr.commit()
            # Delete processed files
            ftp.cwd(company.edifact_supplier_invoice_import_path)
            for filename in ftp.nlst():
                if not filename.endswith('.edi'):
                    continue
                elif filename in results.get('processed'):
                    ftp.delete(filename)

    def parse_edi_file(self, data):
        """Parse the EDI file and return a dict with invoices values."""
        invoice_values = []
        temp_invoice_values = {}
        temp_invoice_line_values = []
        chunk = ''
        for line in data.readlines():
            chunk += line
            if line.startswith('100'):
                supplier_invoice_number = line[3:38].rstrip()
                edi_raw_invoice_type = line[46:47]
                if edi_raw_invoice_type == 'F':
                    invoice_type = 'in_invoice'
                elif edi_raw_invoice_type == 'A':
                    invoice_type = 'in_refund'
                else:
                    invoice_type = False
                date_invoice = line[38:46]
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
                invoice_values.append((temp_invoice_values, chunk))
                chunk = ''
                temp_invoice_values = {}
                temp_invoice_line_values = []

        return invoice_values

    def create_or_update_invoices(self, cr, uid, edi_file_invoice_dict,
                                  context=None):
        """Update invoice or create refund according to the invoice type."""
        processed = []
        successful = []
        failing = []
        for filename, edi_invoices in edi_file_invoice_dict.iteritems():
            for edi_invoice_values, chunk in edi_invoices:
                cr.execute('SAVEPOINT edi_invoice')
                try:
                    if edi_invoice_values.get('invoice_type') == 'in_invoice':
                        document = self.update_invoices(
                            cr, uid, edi_invoice_values, context=context)
                    elif edi_invoice_values.get('invoice_type') == \
                            'in_refund':
                        document = self.create_refund(
                            cr, uid, edi_invoice_values, context=context)
                    else:
                        raise EdifactPurchaseInvoiceParsingError(
                            _('Purchase %s / Invoice %s : Invoice type on the '
                              'EDI file is incorrect.') % (
                                edi_invoice_values.get('purchase_number'),
                                edi_invoice_values.get(
                                    'supplier_invoice_number')
                            ))
                except Exception as e:
                    cr.execute('ROLLBACK TO SAVEPOINT edi_invoice')
                    failing.append((chunk, e))
                else:
                    cr.execute('RELEASE SAVEPOINT edi_invoice')
                    successful.append((chunk, document))
            processed.append(filename)
        return {
            'processed': processed,
            'successful': successful,
            'failing': failing,
        }

    def update_invoices(self, cr, uid, edi_invoice_values, context=None):
        """Update existing invoices with new lines from the EDI files dict.
        Validate if ok or raise an error if something unexpected happens."""
        invoice_obj = self.pool['account.invoice']
        invoice_line_obj = self.pool['account.invoice.line']
        # Find the invoice and update it
        invoice = self._find_invoice(cr, uid, edi_invoice_values.get(
            'purchase_number'), edi_invoice_values.get(
            'supplier_invoice_number'), context=context)
        invoice_vals = self._prepare_invoice_values(cr, uid,
                                                    edi_invoice_values)
        # Check if products are on the invoice
        edi_products_codes_dict = self._get_code_products_dict(
            cr, uid, edi_invoice_values.get('lines'),
            edi_invoice_values.get('purchase_number'),
            edi_invoice_values.get('supplier_invoice_number'), context=context)
        self._check_products_on_invoice(
            cr, uid, invoice, edi_products_codes_dict,
            edi_invoice_values.get('purchase_number'),
            edi_invoice_values.get('supplier_invoice_number'), context=context)
        # Delete existing invoice lines
        invoice_line_ids = [il.id for il in invoice.invoice_line]
        invoice_line_obj.unlink(cr, uid, invoice_line_ids, context=context)
        # Rebrowse the invoice record to refresh the recordset so it does not
        # contain the unlinked lines
        invoice = invoice_obj.browse(cr, uid, invoice.id, context=context)
        # Prepare and write new invoice lines
        invoice_lines_vals = self._prepare_new_invoice_lines(
            cr, uid, edi_invoice_values.get('lines'),
            edi_products_codes_dict, context=context)
        for invoice_line_vals in invoice_lines_vals:
            invoice_line_vals.update(self._call_line_onchanges(
                cr, uid, invoice_line_vals, 'in_invoice', context=context))
        invoice_vals.update({
            'invoice_line': [(0, False, vals) for vals in invoice_lines_vals],
        })
        invoice_obj.write(cr, uid, invoice.id, invoice_vals, context=context)
        # Check subtotals
        different_subtotals = self._check_different_lines_subtotals(
            cr, uid, invoice, context=context)
        if different_subtotals:
            raise EdifactPurchaseInvoiceTotalDifference(_(
                'Purchase %s / Invoice %s : Different subtotals between the '
                'imported EDI and updated invoice for these product codes') % (
                    edi_invoice_values.get('purchase_number'),
                    edi_invoice_values.get('supplier_invoice_number')
            ), different_subtotals)
        # Validate if all went well
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'account.invoice',
                                invoice.id, 'invoice_open', cr)
        return invoice

    def create_refund(self, cr, uid, edi_invoice_values, context=None):
        """Create new refund with data from the EDI files dict"""
        invoice_obj = self.pool['account.invoice']
        refund_vals = self._prepare_refund(cr, uid, edi_invoice_values,
                                           context=context)
        # call onchange_partner_id
        refund_vals.update(invoice_obj.onchange_partner_id(
            cr, uid, [], 'in_refund', refund_vals.get('partner_id'),
            date_invoice=refund_vals.get('date_invoice'),
            company_id=self._get_company(cr, uid, context=context).id
        ).get('value'))

        # prepare lines
        edi_products_codes_dict = self._get_code_products_dict(
            cr, uid, edi_invoice_values.get('lines'),
            edi_invoice_values.get('purchase_number'),
            edi_invoice_values.get('supplier_invoice_number'), context=context)
        refund_lines_vals = self._prepare_refund_lines(
            cr, uid, edi_invoice_values.get('lines'), edi_products_codes_dict,
            context=context)
        for refund_line_vals in refund_lines_vals:
            refund_line_vals.update(self._call_line_onchanges(
                cr, uid, refund_line_vals, 'in_refund', context=context))
        refund_vals.update({
            'invoice_line': [(0, False, vals) for vals in refund_lines_vals],
        })
        # create and return
        refund_id = invoice_obj.create(cr, uid, refund_vals, context=context)
        return invoice_obj.browse(cr, uid, refund_id, context=context)

    def handle_failures(self, cr, uid, failures, context=None):
        """Create a crm.claim with error message and add failed EDI chunks
        as attachment."""
        company = self._get_company(cr, uid, context=context)
        categ_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'debonix_supplier_invoice_edi',
            'crm_category_sogedesca')[1]
        edi_error_file = StringIO()
        # Merge failed chunks and error messages
        error_messages = []
        for chunk, error in failures:
            edi_error_file.write(chunk)
            error_message = error.message
            if not isinstance(error_message, str):
                error_message = error_message.encode('utf-8')
            error_messages.append(error_message)
        edi_error_file.seek(0)
        # Create a claim
        claim_vals = {
            'name': _('EDI supplier invoice error'),
            'categ_id': categ_id,
            'user_id': company.edifact_supplier_invoice_claim_user_id.id,
            'description': '\n'.join(error_messages),
            'claim_type': 'other',
        }
        claim_id = self.pool['crm.claim'].create(cr, uid, claim_vals,
                                                 context=context)
        # Add merged chunks as attachment
        self.pool['ir.attachment'].create(cr, uid, {
            'name': '%s-fail.edi' % fields.date.today(),
            'res_model': 'crm.claim',
            'res_id': claim_id,
            'datas': base64.encodestring(edi_error_file.read()),
            'datas_fname': '%s-fail.edi' % fields.date.today(),
        }, context=context)
        edi_error_file.seek(0)
        return edi_error_file

    def handle_successes(self, cr, uid, successes, context=None):
        """Merge successful chunks"""
        edi_success_file = StringIO()
        for chunk, doc in successes:
            edi_success_file.write(chunk)
        edi_success_file.seek(0)
        return edi_success_file

    def _get_company(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        return user.company_id

    def _find_invoice(self, cr, uid, purchase_number, supplier_invoice_number,
                      context=None):
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
                _('Purchase %s / Invoice %s : Purchase order not found') % (
                    purchase_number, supplier_invoice_number))

        purchase_order = purchase_order_obj.browse(
            cr, uid, purchase_order_ids[0], context=context)
        invoices = purchase_order.invoice_ids
        if not invoices:
            raise EdifactPurchaseInvoiceNotFound(
                _('Purchase %s / Invoice %s : No invoice found for the '
                  'purchase order') % (purchase_number,
                                       supplier_invoice_number))
        elif len(invoices) > 1:
            raise EdifactPurchaseInvoiceNotFound(
                _('Purchase %s / Invoice %s : Multiple invoices found for the '
                  'same purchase order') % (purchase_number,
                                            supplier_invoice_number))
        return invoices[0]

    def _prepare_invoice_values(self, cr, uid, edi_invoice_values,
                                context=None):
        return {
            'supplier_invoice_number': edi_invoice_values.get(
                'supplier_invoice_number'),
            'date_invoice': edi_invoice_values.get('date_invoice'),
            'date_due': edi_invoice_values.get('date_due'),
        }

    def _get_code_products_dict(self, cr, uid, edi_line_values,
                                purchase_number, supplier_invoice_number,
                                context=None):
        """Return a dict matching product_code from the EDI values with the
        products from the invoice.
        Raise an error if no existing product is found for the product_code.
        """
        edi_product_codes = [
                l.get('product_code').lstrip('0') for l in edi_line_values]
        # search on product.supplierinfo product_code first
        product_obj = self.pool['product.product']
        product_supplierinfo_obj = self.pool['product.supplierinfo']
        product_supplier_ids = product_supplierinfo_obj.search(cr, uid, [
            ('product_code', 'in', edi_product_codes)], context=context)
        if len(product_supplier_ids) == 1:
            products_sup = product_supplierinfo_obj.read(
                cr, uid, product_supplier_ids, [
                    'product_code', 'product_id'], context=context)
            edi_products_codes_dict = {
                    p['product_code']: p['product_id'][
                        0] for p in products_sup}
        else:
            edi_products_codes_dict = {}
        # Get the products not found
        not_found_on_supplierinfo = [
                code for code in edi_product_codes
                if code not in edi_products_codes_dict]
        if not_found_on_supplierinfo:
            # search on product.product default_code
            product_ids = product_obj.search(cr, uid, [
                ('default_code', 'in', not_found_on_supplierinfo)],
                context=context)
            products = product_obj.read(cr, uid, product_ids, ['default_code'],
                                        context=context)
            # add found products to edi_products_code_dict
            for p in products:
                edi_products_codes_dict[p['default_code']] = p['id']
        else:
            # We will get the product.product instead of the product_template
            for product_default_code, template_id in\
                    edi_products_codes_dict.iteritems():
                product_id = product_obj.search(cr, uid, [('product_tmpl_id',
                                                          '=', template_id)],
                                                context=context)
                edi_products_codes_dict.update(
                    {product_default_code: product_id[0]})

        not_found_product_codes = set(edi_product_codes) - set(
            edi_products_codes_dict.keys())
        if not_found_product_codes:
            raise EdifactPurchaseInvoiceProductNotFound(
                _('Purchase %s / Invoice %s : EDI products codes not found in '
                  'the system') % (purchase_number, supplier_invoice_number),
                list(not_found_product_codes)
            )
        return edi_products_codes_dict

    def _check_products_on_invoice(self, cr, uid, invoice,
                                   edi_products_codes_dict, purchase_number,
                                   supplier_invoice_number, context=None):
        """Raise an error if the product is not on the invoice."""
        invoice_product_ids = [l.product_id.id for l in invoice.invoice_line]
        edi_product_codes_ids = [
                l for l in edi_products_codes_dict.values()]
        not_found_products = set(edi_product_codes_ids) - set(
            invoice_product_ids)
        if not_found_products:
            raise EdifactPurchaseInvoiceProductNotFound(
                _('Purchase %s / Invoice %s : EDI products not found on the '
                  'invoice') % (purchase_number, supplier_invoice_number,),
                list(not_found_products)
            )

    def _prepare_new_invoice_lines(self, cr, uid, edi_lines,
                                   edi_products_codes_dict, context=None):
        """Prepare invoice line to create according to EDI lines"""
        invoice_line_vals = []
        for edi_line in edi_lines:
            product_id = edi_products_codes_dict.get(
                edi_line.get('product_code').lstrip('0'))
            product = self.pool['product.product'].browse(cr, uid, product_id,
                                                          context=context)
            account = product.property_account_expense

            if not account:
                account = product.categ_id and \
                          product.categ_id.property_account_expense_categ\
                          or False
            if not account:
                raise osv.except_osv(
                    _('Error!'),
                    _('Define expense account for this product: '
                      '"%s" (id:%d).') % (product.name, product.id,))
            vals = {
                'product_id': product.id,
                'quantity': edi_line.get('quantity'),
                'price_unit': edi_line.get('price_unit'),
                'account_id': account.id,
                'uos_id': product.uos_id.id,
                'edi_line_amount': edi_line.get('line_amount')
            }
            invoice_line_vals.append(vals)
        return invoice_line_vals

    def _call_line_onchanges(self, cr, uid, line_vals, invoice_type,
                             context=None):
        """Plays product_id_change on prepared line vals."""
        invoice_line_obj = self.pool['account.invoice.line']
        company = self._get_company(cr, uid, context=context)
        partner = company.edifact_supplier_invoice_partner_id
        currency_eur_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'base', 'EUR')[1]
        # Call product onchange
        changed_vals = invoice_line_obj.product_id_change(
            cr, uid, [], line_vals.get('product_id'),
            line_vals.get('uos_id'),
            qty=line_vals.get('quantity'),
            type=invoice_type,
            partner_id=partner.id,
            fposition_id=partner.property_account_position.id,
            price_unit=line_vals.get('price_unit'),
            currency_id=currency_eur_id,
            context=context, company_id=company.id
        ).get('value')
        # Remove changed price unit to ensure the price in EDI file is used
        if 'invoice_line_tax_id' in changed_vals:
            changed_vals.update({'invoice_line_tax_id': [
                (6, 0, changed_vals['invoice_line_tax_id'])]})
        changed_vals.pop('price_unit')
        changed_vals.pop('account_id')
        return changed_vals

    def _check_different_lines_subtotals(self, cr, uid, invoice, context=None):
        """Check if price_subtotal of lines matches theirs edi_line_amount."""
        error_lines = []
        precision = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account')
        for invoice_line in invoice.invoice_line:
            if float_compare(invoice_line.edi_line_amount,
                             invoice_line.price_subtotal,
                             precision_digits=precision) != 0:
                error_lines.append(invoice_line)
        return error_lines

    def _prepare_refund(self, cr, uid, edi_invoice, context=None):
        """Prepare refund to create according to EDI file"""
        company = self._get_company(cr, uid, context=context)
        currency_eur_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'base', 'EUR')[1]
        return {
            'partner_id': company.edifact_supplier_invoice_partner_id.id,
            'origin': edi_invoice.get('purchase_number'),
            'supplier_invoice_number': edi_invoice.get(
                'supplier_invoice_number'),
            'reference_type': 'none',
            'name': edi_invoice.get('purchase_number'),
            'date_invoice': edi_invoice.get('date_invoice'),
            'date_due': edi_invoice.get('date_due'),
            'type': 'in_refund',
            'currency_id': currency_eur_id
        }

    def _prepare_refund_lines(self, cr, uid, edi_lines,
                              edi_products_codes_dict, context=None):
        """Prepare refund line to create according to EDI lines"""
        lines_vals = []
        for edi_line in edi_lines:
            product_id = edi_products_codes_dict.get(
                edi_line.get('product_code').lstrip('0'))
            product = self.pool['product.product'].browse(cr, uid, product_id,
                                                          context=context)
            account = product.property_account_expense or \
                product.categ_id.property_account_expense_categ
            if not account:
                raise osv.except_osv(
                    _('Error!'),
                    _('Define expense account for this product: '
                      '"%s" (id:%d).') % (product.name, product.id,))

            vals = {
                'product_id': product.id,
                'quantity': edi_line.get('quantity'),
                'price_unit': edi_line.get('price_unit'),
                'account_id': account.id,
                'uos_id': product.uos_id.id,
            }
            lines_vals.append(vals)
        return lines_vals
