# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Straight port of XLS to CSV report without refactoring"""
from contextlib import closing
import StringIO
import unicodecsv as csv

from openerp import pooler
from openerp.report.report_sxw import report_sxw
from openerp.addons.account_financial_report_webkit.report.partner_balance \
    import PartnerBalanceWebkit


def display_line(all_comparison_lines):
    return any([line.get('balance') for line in all_comparison_lines])


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ReportCSV(report_sxw):
    """Custom report class to output CSV base on webkit report_xls"""
    def create(self, cr, uid, ids, data, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        self.cr = cr
        self.uid = uid
        report_obj = self.pool.get('ir.actions.report.xml')
        report_ids = report_obj.search(
            cr, uid, [('report_name', '=', self.name[7:])], context=context)
        if report_ids:
            report_xml = report_obj.browse(
                cr, uid, report_ids[0], context=context)
            self.title = report_xml.name
            if report_xml.report_type == 'csv':
                return self.create_source_csv(cr, uid, ids, data,
                                              report_xml, context)
        elif context.get('csv_export'):
            # use model from 'data' when no ir.actions.report.xml entry
            self.table = data.get('model') or self.table
            return self.create_source_csv(cr, uid, ids, data, context)
        return super(ReportCSV, self).create(cr, uid, ids, data, context)

    def create_source_csv(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context = {}
        parser_instance = self.parser(cr, uid, self.name2, context)
        self.parser_instance = parser_instance
        self.context = context
        objs = self.getObjects(cr, uid, ids, context)
        parser_instance.set_context(objs, data, ids, 'csv')
        objs = parser_instance.localcontext['objects']
        _p = AttrDict(parser_instance.localcontext)
        csv = self.generate_csv(_p, data, objs)
        return (csv, 'csv')


class PartnerBalanceCSV(ReportCSV):
    def format_parameters(self, _p):
        def _format(val):
            try:
                return val['name']
            except Exception:
                return val

        output = []
        params = [
            'start_period',
            'stop_period',
            'start_date',
            'stop_date',
            'comp_params',
            'fiscalyear',
            'comparison_mode',
            'initial_balance_mode',
            'report_name',
        ]
        for param in params:
            if param == 'comp_params':
                for ind, comp_params in enumerate(_p.comp_params):
                    for inner_param in comp_params:
                        output.append("comparaison_{}_{}:{}".format(
                            ind,
                            inner_param,
                            _format(comp_params[inner_param]),
                        ))
            else:
                output.append("{}:{}".format(param, _format(_p[param])))

        return "; ".join(output)

    def generate_csv(self, _p, data, objects):
        with closing(StringIO.StringIO()) as csvfile:
            # report_parameters = TODO do we really want these ?
            params = self.format_parameters(_p)
            field_names = ['Account/Partner_name', 'Code/Ref',
                           'Initial balance', 'Debit', 'Credit', 'Balance']

            csv_writer = csv.DictWriter(csvfile, fieldnames=field_names,
                                        delimiter='|')
            params = self.format_parameters(_p)
            csv_writer.writerow({'Account/Partner_name': params})
            csv_writer.writeheader()
            for current_account in objects:
                partners_order = current_account.partners_order
                # do not display accounts without partners
                if not partners_order:
                    continue

                current_partner_amounts = current_account.partners_amounts
                total_initial_balance = 0.0
                total_debit = 0.0
                total_credit = 0.0
                total_balance = 0.0

                for (partner_code_name, partner_id, partner_ref, partner_name)\
                        in partners_order:
                    partner = current_partner_amounts.get(partner_id, {})
                    total_initial_balance += partner.get('init_balance', 0.0)
                    total_debit += partner.get('debit', 0.0)
                    total_credit += partner.get('credit', 0.0)
                    total_balance += partner.get('balance', 0.0)

                    row = {
                        'Account/Partner_name': partner_name or 'Unallocated',
                        'Code/Ref': partner_ref or '',
                        'Initial balance': partner.get('init_balance', 0.0),
                        'Debit': partner.get('debit', 0.0),
                        'Credit': partner.get('credit', 0.0),
                        'Balance': partner['balance'] if partner else 0.0
                    }

                    csv_writer.writerow(row)
                init_bal = _p['initial_balance_mode']
                balance_row = {
                        'Account/Partner_name': current_account.name,
                        'Code/Ref': current_account.code,
                        'Initial balance': total_initial_balance if init_bal else 0.0, # noqa
                        'Debit': total_debit,
                        'Credit': total_credit * -1,
                        'Balance': total_balance
                    }
                csv_writer.writerow(balance_row)

            return csvfile.getvalue()


PartnerBalanceCSV('report.account.account_report_partner_balance_csv',
                  'account.account',
                  parser=PartnerBalanceWebkit)
