# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.addons.decimal_precision as dp
from openerp.osv import orm, fields, osv


class AccountInvoiceLine(osv.osv):

    _inherit = 'account.invoice.line'

    _columns = {
        'edi_line_amount': fields.float(
            'EDI line amount',
            digits_compute=dp.get_precision('Account'))
    }
