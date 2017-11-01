# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import fields, orm


class AccountPartnerBalanceWizard(orm.TransientModel):

    _inherit = "partner.balance.webkit"

    def csv_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('csv_export'):
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_partner_balance_csv',
                'datas': data}
        else:
            return super(AccountPartnerBalanceWizard, self)._print_report(
                cr, uid, ids, data, context=context)
