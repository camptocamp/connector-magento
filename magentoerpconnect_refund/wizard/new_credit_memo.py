# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class new_credit_memo(orm.TransientModel):
    _name = "new.credit.memo"

    _columns = {
        'credit_amount': fields.float(
            'Credit note amount',
            digits_compute=dp.get_precision('Account')),
    }

    def _get_amount(self, cr, uid, context=None):
        invoice_obj = self.pool['account.invoice']
        res = 0
        if context is None:
            context = {}
        if context.get('active_id'):
            refund = invoice_obj.browse(cr, uid, context['active_id'],
                                        context=context)
            res = invoice_obj._get_refund_amount(cr, uid, refund,
                                                 context=context)
        return res

    _defaults = {
        'credit_amount': _get_amount,
        }

    def new_credit_memo(self, cr, uid, ids, context=None):
        invoice_obj = self.pool['account.invoice']
        if context is None:
            context = {}
        if context.get('active_id'):
            wizard = self.browse(cr, uid, ids[0], context=context)
            refund = invoice_obj.browse(
                cr, uid, context['active_id'], context=context)
            invoice_obj._create_credit_memo(
                cr, uid, refund, wizard.credit_amount, context=context)
        return {'type': 'ir.actions.act_window_close'}
