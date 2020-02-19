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


class sale_new_credit_note(orm.TransientModel):
    _inherit = "sale.new.credit.note"

    _columns = {
        'magento_credit_memo': fields.boolean(
            'Create Magento credit memo',
            help="If checked, a credit memo will be created in Magento with "
                 "the selected amount."),
    }

    def new_credit_note(self, cr, uid, ids, context=None):
        invoice_obj = self.pool['account.invoice']
        if context is None:
            context = {}
        res = super(sale_new_credit_note, self).new_credit_note(
            cr, uid, ids, context=context)
        wizard = self.browse(cr, uid, ids[0], context=context)
        if context.get('active_id') and wizard.magento_credit_memo:
            refund = invoice_obj.browse(
                cr, uid, context['active_id'], context=context)
            invoice_obj._create_credit_memo(
                cr, uid, refund, wizard.credit_amount, context=context)
        return res
