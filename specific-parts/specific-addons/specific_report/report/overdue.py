# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw


class Overdue(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Overdue, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
            'getLines': self._lines_get,
            'message': self._message,
        })
        self.context = context

    def _lines_get(self, partner):
        moveline_obj = self.pool['account.move.line']
        partner = partner.commercial_partner_id
        movelines = moveline_obj.search(
            self.cr, self.uid,
            [('partner_id', '=', partner.id),
             ('account_id.type', 'in', ['receivable', 'payable']),
             ('account_id.be_follow_up', '=', False),
             ('state', '<>', 'draft'),
             ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(self.cr, self.uid, movelines,
                                        context=self.context)
        return movelines

    def _message(self, obj, company):
        company_pool = self.pool['res.company']
        ctx = self.context.copy()
        ctx['lang'] = obj.lang
        message = company_pool.browse(self.cr, self.uid,
                                      company.id,
                                      context=ctx).overdue_msg
        return message


report_sxw.report_sxw('report.account.overdue.c2c', 'res.partner',
                      'addons/specific_report/report/overdue.rml',
                      parser=Overdue)
