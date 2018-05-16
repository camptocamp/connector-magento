# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from StringIO import StringIO
from openerp.tests.common import TransactionCase
from openerp import netsvc


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

        # Company settings
        admin_user = res_users_obj.browse(cr, uid, uid)
        company = admin_user.company_id
        claim_user_id = res_users_obj.copy(cr, uid, uid)
        country_france_id = self.model_data_obj.get_object_reference(
            cr, uid, 'base', 'fr')[1]
        crm_case_categ_id = self.model_data_obj.get_object_reference(
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
            'edifact_supplier_invoice_claim_cat_id': crm_case_categ_id,
            'edifact_supplier_invoice_claim_user_id': claim_user_id,
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

    def test_edi_import(self):
        cr, uid = self.cr, self.uid
        invoice_values = {}
        demo_edi_path = '../../specific-parts/specific-addons/' \
                        'debonix_supplier_invoice_edi/demo/demo.edi'
        with open(demo_edi_path, 'r') as edi_file:
            data = StringIO()
            data.write(edi_file.read())
            data.seek(0)
            invoice_values['demo.edi'] = self.edi_import_obj.import_edi_file(
                data)
        self.edi_import_obj.update_invoices(cr, uid, invoice_values)
        self.assertEqual(self.invoice.supplier_invoice_number, 'INV00000001')
        self.assertEqual(self.invoice.state, 'open')
        self.assertEqual(len(self.invoice.invoice_line), 2)
