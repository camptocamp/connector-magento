# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#    Copyright 2012 Camptocamp SA
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
###############################################################################

import time
import StringIO
import base64

from openerp.osv import orm, fields
import unicodecsv


class cutoff_report_wizard(orm.TransientModel):
    _name = 'cutoff.report.wizard'
    _description = 'Export Stock values details for a location'

    _columns = {
        'report_type': fields.selection([('in', 'Incoming cut-off'),
                                         ('out', 'Outgoing cut-off')],
                                        'Report type',
                                        required=True),
        'cutoff_date': fields.date('Cutoff date', required=True),
        'data': fields.binary('CSV', readonly=True),
        'state': fields.selection([('draft', 'Draft'),
                                   ('done', 'Done')],
                                  string='State'),
    }

    _defaults = {
        'state': 'draft',
        'report_type': 'out',
        'cutoff_date': fields.date.context_today
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        rows = self.get_data(cr, uid, ids, context)

        file_data = StringIO.StringIO()
        try:
            writer = unicodecsv.writer(file_data, encoding='utf-8')
            writer.writerows(rows)
            file_value = file_data.getvalue()
            self.write(cr, uid, ids,
                       {'data': base64.encodestring(file_value),
                        'state': 'done'},
                       context=context)
        finally:
            file_data.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }

    def _get_incoming_cutoff(self, cr, uid, ids, cutoff_date,
                             context=None):
        cutoff_date = cutoff_date or time.strftime('%Y-%m-%d %H:%M:%S')
        cr.execute("""
            SELECT sp.name, pp.default_code, sm.name,
                   CAST(sm.product_qty AS int), pt.standard_price,
                   (CAST(sm.product_qty AS int) * pt.standard_price) as total
            FROM stock_move sm
            INNER JOIN product_product pp
                ON sm.product_id = pp.id
            INNER JOIN product_template pt
                ON pt.id = pp.product_tmpl_id
            INNER JOIN stock_picking sp
                ON sp.id = sm.picking_id
            WHERE sm.state = 'done'
              AND sm.location_id = 7
              AND sm.location_dest_id = 11
              AND sp.invoice_state = '2binvoiced'
              AND sm.product_qty != 0
              AND sp.date_done <= %(cutoff_date)s
            ORDER BY sp.name""",
                   {'cutoff_date': cutoff_date})
        return cr.fetchall()

    def _get_outgoing_cutoff(self, cr, uid, ids, cutoff_date,
                             context=None):
        cutoff_date = cutoff_date or time.strftime('%Y-%m-%d %H:%M:%S')
        cr.execute("""
            SELECT sp.name, pp.default_code, sm.name,
            CAST(sm.product_qty AS int), pt.standard_price,
            (CAST(sm.product_qty AS int) * pt.standard_price) as total
            FROM stock_move sm
            INNER JOIN product_product pp
                ON sm.product_id = pp.id
            INNER JOIN product_template pt
                ON pt.id = pp.product_tmpl_id
            INNER JOIN stock_picking sp
                ON sp.id = sm.picking_id
            INNER JOIN sale_order so
                ON sp.sale_id = so.id
            LEFT OUTER JOIN sale_order_invoice_rel soir
                ON so.id = soir.order_id
            LEFT OUTER JOIN account_invoice ai
                ON ai.id = soir.invoice_id
            WHERE sm.state = 'done'
              AND sm.location_id = 11
              AND sm.location_dest_id = 8
            AND (sp.date_done IS NULL
              OR sp.date_done <= %(cutoff_date)s
            )
            AND (ai.date_invoice IS NULL
              OR ai.date_invoice > %(cutoff_date)s
            )
            AND (ai.state IS NULL
              OR ai.state NOT IN ('draft', 'proforma2', 'cancel')
            )
            ORDER BY sp.name""",
                   {'cutoff_date': cutoff_date})
        return cr.fetchall()

    def _get_header(self, cr, uid, ids, context=None):
        return [u'picking_name',
                u'default_code',
                u'name',
                u'quantity',
                u'standard_price',
                u'total']

    def get_data(self, cr, uid, ids, context=None):
        context = context or {}
        context['lang'] = 'fr_FR'

        rows = []
        rows.append(self._get_header(cr, uid, ids, context=context))
        form = self.browse(cr, uid, ids[0], context=context)

        if form.report_type == 'out':
            rows.extend(self._get_outgoing_cutoff(
                cr, uid, ids, form.cutoff_date, context=context)
            )
        else:
            rows.extend(self._get_incoming_cutoff(
                cr, uid, ids, form.cutoff_date, context=context)
            )
        return rows
