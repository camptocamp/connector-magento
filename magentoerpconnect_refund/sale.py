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
from openerp.addons.magentoerpconnect.backend import magento
from openerp.addons.magentoerpconnect.sale import SaleOrderImportMapper


class sale_order(orm.Model):
    _inherit = "sale.order"

    def get_credit_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context['manual_credit_line'] = True
        return super(sale_order, self).get_credit_lines(
            cr, uid, ids, context=context)


@magento(replacing=SaleOrderImportMapper)
class SaleOrderRefundImportMapper(SaleOrderImportMapper):
    _model_name = 'magento.sale.order'

    def _add_refund_lines(self, map_record, values):
        amount = float(map_record.source['customer_balance_amount'])
        if amount:
            lines = self.session.pool['sale.order']._get_credit_lines(
                self.session.cr, self.session.uid, values['partner_id'],
                amount, context=self.session.context)
            assert lines, ("A refund has been selected in Magento but "
                           "there is no refund available in the ERP for "
                           "this customer.")
            available_amount = 0
            for line in lines:
                available_amount += line[2]['amount']
            assert available_amount is not amount, (
                "All credit memo has already been used for this customer.")
            values['credit_line_ids'] = lines
        return values

    def finalize(self, map_record, values):
        values = super(SaleOrderRefundImportMapper, self).finalize(map_record,
                                                                   values)
        values = self._add_refund_lines(map_record, values)
        return values
