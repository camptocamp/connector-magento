# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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

import base64
import os
import logging
import string

from openerp.osv import orm, fields
from openerp.tools.translate import _
from ..stockit_exporter.exporter import StockitExporter


_logger = logging.getLogger()


def make_string_valid_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)


class StockItInPickingExport(orm.TransientModel):
    _name = 'stockit.export.in.picking'
    _description = 'Export incoming pickings in Stock iT format'

    _columns = {
        'data': fields.binary('File', readonly=True),
        'state': fields.selection([('draft', 'Draft'),
                                   ('empty', 'Empty'),
                                   ('done', 'Done')],
                                  string='State'),
    }

    _defaults = {
        'state': 'draft',
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        rows = self.get_data(cr, uid, ids, context)
        exporter = StockitExporter()
        data = exporter.get_csv_data(rows)
        if data:
            self.write(cr, uid, ids,
                       {'data': base64.encodestring(data),
                        'state': 'done'},
                       context=context)
        else:
            self.write(cr, uid, ids,
                       {'state': 'empty'},
                       context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }

    def create_request_error(self, cr, uid, err_msg, context=None):
        _logger.info("Error exporting ingoing pickings file: %s", err_msg)

        # TODO post a message
        request = self.pool.get('res.request')
        summary = _("Stock-it ingoing pickings failed\n"
                    "With error:\n"
                    "%s") % (err_msg,)

        request.create(cr, uid,
                       {'name': _("Stock-it ingoing pickings export"),
                        'act_from': uid,
                        'act_to': uid,
                        'body': summary,
                        })
        return True

    def run_background_export(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_base_path or not company.stockit_in_picking_export:
            raise orm.except_orm(
                _('Error'),
                _('Stockit path is not configured on company.'))
        filename = "in_picking_export_with_id.csv"
        filepath = os.path.join(company.stockit_base_path,
                                company.stockit_in_picking_export,
                                filename)
        try:
            rows = self.get_data(cr, uid, [], context)
            exporter = StockitExporter(filepath)
            data = exporter.get_csv_data(rows)
            exporter.export_file(data)
        except Exception as e:
            self.create_request_error(cr, uid, str(e), context)
        return True

    def get_data(self, cr, uid, ids, context=None):
        """Export incoming pickings in Stock iT format"""
        picking_obj = self.pool.get('stock.picking')
        context = context or {}
        context['lang'] = 'fr_FR'

        rows = []
        picking_ids = picking_obj.search(cr, uid,
                                         [('type', '=', 'in'),
                                          ('state', '=', 'assigned')],
                                         context=context)
        for picking in picking_obj.browse(cr, uid, picking_ids, context=context):
            address = picking.address_id
            if address.partner_id:
                partner_name = address.partner_id.name
            else:
                partner_name = address.name or ''

            name = picking.name
            if picking.origin:
                name += '-' + picking.origin
            name = make_string_valid_filename(name)
            for line in picking.move_lines:
                if line.product_id.type == 'service':
                    continue  # skip service products
                row = [
                    'E',  # type
                    str(picking.id),  # unique id
                    name[:18],  # ref/name
                    line.date,  # expected date
                    line.product_id.default_code,  # product code
                    partner_name[:20],  # product supplier name
                    str(line.product_qty),  # quantity
                    '',  # 6 empty fields for the return of stock it
                    '',
                    '',
                    '',
                    '',
                    '',
                ]
                rows.append(row)
        return rows
