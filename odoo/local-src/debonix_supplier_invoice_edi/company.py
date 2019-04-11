# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.osv import fields, orm


class ResCompany(orm.Model):

    _inherit = 'res.company'

    _columns = {
        'edifact_supplier_invoice_amount_difference': fields.float(),
        'edifact_supplier_invoice_days': fields.integer(),
        'edifact_supplier_invoice_partner_id': fields.many2one('res.partner'),
        'edifact_supplier_invoice_user_id': fields.many2one('res.users'),
        'edifact_supplier_invoice_intrastat_country_id':
            fields.many2one('res.country'),
        'edifact_supplier_invoice_claim_cat_id':
            fields.many2one('crm.case.categ'),
        'edifact_supplier_invoice_claim_user_id':
            fields.many2one('res.users'),
    }
