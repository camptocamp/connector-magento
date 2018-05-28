# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from StringIO import StringIO
from openerp.modules import get_module_resource
from openerp.tests.common import TransactionCase
from openerp import netsvc
from ..edi_import_supplier_invoice import (
    EdifactPurchaseInvoiceParsingError,
    EdifactPurchaseInvoiceNotFound,
    EdifactPurchaseInvoiceProductNotFound,
    EdifactPurchaseInvoiceTotalDifference,
)


class TestEDIImport(TransactionCase):

    def setUp(self):

        super(TestEDIImport, self).setUp()
        cr, uid = self.cr, self.uid
        res_users_obj = self.registry('res.users')
        self.model_data_obj = self.registry('ir.model.data')
        self.wf_service = netsvc.LocalService('workflow')
        self.stock_picking_obj = self.registry('stock.picking')
        self.purchase_order_obj = self.registry('purchase.order')
        self.account_invoice_obj = self.registry('account.invoice')
        self.product_obj = self.registry('product.product')
        self.edi_import_obj = self.registry('edi.import.supplier.invoice')
        self.claim_obj = self.registry('crm.claim')
        self.attachment_obj = self.registry('ir.attachment')
        # Company settings
        admin_user = res_users_obj.browse(cr, uid, uid)
        company = admin_user.company_id
        self.claim_user_id = res_users_obj.copy(cr, uid, uid)
        country_france_id = self.model_data_obj.get_object_reference(
            cr, uid, 'base', 'fr')[1]
        self.crm_case_categ_id = self.model_data_obj.get_object_reference(
            cr, uid, 'debonix_supplier_invoice_edi',
            'crm_category_sogedesca')[1]
        self.sogedesca_partner_id = self.model_data_obj.get_object_reference(
            cr, uid, 'debonix_supplier_invoice_edi', 'sogedesca')[1]
        self.registry('res.company').write(cr, uid, company.id, {
            'edifact_supplier_invoice_partner_id': self.sogedesca_partner_id,
            'edifact_supplier_invoice_amount_difference': 0.1,
            'edifact_supplier_invoice_days': 90,
            'edifact_supplier_invoice_user_id': uid,
            'edifact_supplier_invoice_intrastat_country_id': country_france_id,
            'edifact_supplier_invoice_claim_cat_id': self.crm_case_categ_id,
            'edifact_supplier_invoice_claim_user_id': self.claim_user_id,
        })

        # Create the purchase order
        self.product_111111111_id = self.model_data_obj.get_object_reference(
            cr, uid, 'debonix_supplier_invoice_edi',
            'product_edi_111111111')[1]
        self.product_222222222_id = self.model_data_obj.get_object_reference(
            cr, uid, 'debonix_supplier_invoice_edi',
            'product_edi_222222222')[1]
        self.product_111111111 = self.product_obj.browse(
            cr, uid, self.product_111111111_id)
        self.product_222222222 = self.product_obj.browse(
            cr, uid, self.product_222222222_id)
        self.stock_location_id = self.model_data_obj.get_object_reference(
            cr, uid, 'stock', 'stock_location_stock')[1]
        self.pricelist_id = self.model_data_obj.get_object_reference(
            cr, uid, 'purchase', 'list0')[1]
        purchase_order_id = self.purchase_order_obj.create(cr, uid, {
            'name': 'TEST_EDI_01',
            'partner_id': self.sogedesca_partner_id,
            'location_id': self.stock_location_id,
            'pricelist_id': self.pricelist_id,
            'order_line': [(0, 0, {
                'product_id': self.product_111111111_id,
                'name': self.product_111111111.description,
                'product_qty': 1,
                'price_unit': 11.1,
                'date_planned': '2018-05-16',
            }), (0, 0, {
                'product_id': self.product_222222222_id,
                'name': self.product_222222222.description,
                'product_qty': 2,
                'price_unit': 22.2,
                'date_planned': '2018-05-16',
            })]
        })
        # Validate to create invoice
        self.wf_service.trg_validate(uid, 'purchase.order', purchase_order_id,
                                     'purchase_confirm', cr)
        # Validate picking
        self.purchase_order_obj.picking_done(cr, uid, purchase_order_id)
        self.purchase_order = self.purchase_order_obj.browse(
            cr, uid, purchase_order_id)
        self.invoice = self.purchase_order.invoice_ids[0]

    def _prepare_import(self, edi_files_list):
        cr, uid = self.cr, self.uid
        invoice_values = {}
        for edi_file_name in edi_files_list:
            edi_file_path = get_module_resource(
                'debonix_supplier_invoice_edi', 'demo', edi_file_name)
            with open(edi_file_path, 'r') as edi_file:
                data = StringIO()
                data.write(edi_file.read())
                data.seek(0)
                invoice_values[edi_file_name] = self.edi_import_obj.\
                    parse_edi_file(data)
        res = self.edi_import_obj.create_or_update_invoices(cr, uid,
                                                            invoice_values)
        return res, invoice_values

    def test_processed(self):
        res, invoice_values = self._prepare_import(['demo_ok.edi',
                                                    'demo_fail.edi'])
        processed = res.get('processed')
        self.assertEqual(len(processed), 2)
        self.assertIn('demo_ok.edi', processed)
        self.assertIn('demo_fail.edi', processed)

    def test_successful(self):
        cr, uid = self.cr, self.uid
        res, invoice_values = self._prepare_import(['demo_ok.edi'])
        successful = res.get('successful')
        self.assertEqual(len(successful), 2)
        success_invoices = [tpl[1] for tpl in successful]
        self.assertIn(self.invoice, success_invoices)
        self.assertEqual(self.invoice.supplier_invoice_number, 'INV00000001')
        self.assertEqual(self.invoice.state, 'open')
        self.assertEqual(len(self.invoice.invoice_line), 2)
        refund_id = self.account_invoice_obj.search(cr, uid, [
            ('supplier_invoice_number', '=', 'REF00000001')])
        refund = self.account_invoice_obj.browse(cr, uid, refund_id)[0]
        self.assertIn(refund, success_invoices)
        self.assertEqual(len(refund.invoice_line), 2)

    def test_failing(self):
        cr, uid = self.cr, self.uid
        res, invoice_values = self._prepare_import(['demo_fail.edi'])
        failing = res.get('failing')
        failed_edi_file = self.edi_import_obj.handle_failures(cr, uid, failing)
        self.assertEqual(len(failing), 4)
        errors = [fail[1] for fail in failing]
        errors_order = [
            EdifactPurchaseInvoiceTotalDifference,
            EdifactPurchaseInvoiceParsingError,
            EdifactPurchaseInvoiceNotFound,
            EdifactPurchaseInvoiceProductNotFound
        ]
        for cnt, error in enumerate(errors):
            self.assertTrue(isinstance(
                error, errors_order[cnt]))
        claim_id = self.claim_obj.search(
            cr, uid, [('categ_id', '=', self.crm_case_categ_id)])[0]
        claim = self.claim_obj.browse(cr, uid, claim_id)
        self.assertEqual(claim.user_id.id, self.claim_user_id)
        self.assertEqual(claim.claim_type, 'other')
        self.assertEqual(claim.description,
                         '\n'.join([str(err) for err in errors]))
        # Check attachment
        attachement_id = self.attachment_obj.search(
            cr, uid, [('res_id', '=', claim_id),
                      ('res_model', '=', 'crm.claim')])[0]
        att = base64.decodestring(
            self.attachment_obj._data_get(cr, uid, [attachement_id], False,
                                          False)[attachement_id])
        self.assertEqual(att, failed_edi_file.read())
