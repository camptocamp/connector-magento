# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi. Copyright Camptocamp SA
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

import time

from report import report_sxw
from osv import osv
from tools.translate import _
import pooler
from operator import add, itemgetter
from itertools import groupby
from datetime import datetime

#from common_report_header_webkit import CommonReportHeaderWebkit
from c2c_webkit_report import webkit_report

class BankStatementWebkit(report_sxw.rml_parse):

    def __init__(self, cursor, uid, name, context):
        super(BankStatementWebkit, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        
        company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('BORDEREAU DE REMISE DE CHEQUES'), company.name, company.currency_id.name))
        statement = self.pool.get('account.bank.statement').browse(cursor,uid,context['active_id']);
        footer_date_time = self.formatLang(str(datetime.today())[:19], date_time=True)
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'get_bank_statement' : self._get_bank_statement_data,
            'report_name': _('BORDEREAU DE REMISE DE CHEQUES'),
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })
    def _get_bank_statement_data(self,statement):
        statement_line_ids = self.pool.get('account.bank.statement.line').search(self.cr,self.uid,[['statement_id','=',statement.id]])
        statement_lines = self.pool.get('account.bank.statement.line').browse(self.cr,self.uid,statement_line_ids)
        return statement_lines
        
webkit_report.WebKitParser('report.specific_report.report_bank_statement_webkit',
                           'account.bank.statement',
                           'addons/specific_report/report/templates/bank_statement_report.mako',
                           parser=BankStatementWebkit)
