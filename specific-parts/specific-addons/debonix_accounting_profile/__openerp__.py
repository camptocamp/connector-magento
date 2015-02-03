# -*- coding: utf-8 -*-
##############################################################################
#
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

{'name': "Debonix Accounting Profile",
 'description': """
Merely replaces l10n_fr_profile. It installs the same modules
but `invoicing_voucher_killer`.
 """,
 'version': "1.0",
 'author': "Camptocamp",
 'category': "Accounting & Finance",
 'website': "http://www.camptocamp.com",
 'depends': [
     'account_accountant',
     'account_constraints',
     'account_default_draft_move',
     'account_draft_invoice_print',
     'account_financial_report_webkit',
     'account_financial_report_webkit_xls',
     'account_journal_report_xls',
     'account_move_line_report_xls',
     'report_xls',
     'account_export_csv',
     'account_reversal',
     'currency_rate_update',
     'account_compute_tax_amount',
     'base_iban',
     'account_move_validation_improvement',
     'account_statement_base_completion',
     'account_statement_base_import',
     'account_statement_ext',
     'account_statement_commission',
     'statement_voucher_killer',
     'account_advanced_reconcile',
     'account_advanced_reconcile_transaction_ref',
     'account_statement_transactionid_completion',
     'account_statement_transactionid_import',
     'l10n_fr',
     'l10n_fr_rib',
     'l10n_fr_siret',
     'l10n_fr_fec',
 ],
 'data': [],
 'installable': True
 }
