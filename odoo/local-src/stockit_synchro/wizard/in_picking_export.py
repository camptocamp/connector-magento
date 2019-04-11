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
from .wizard_utils import post_message
from datetime import datetime


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
        'force_export': fields.boolean(string='Force export',
                                       help="If this field is checked, "
                                            "picking IN with stockit export "
                                            "date will be exported")
    }

    _defaults = {
        'state': 'draft',
        'force_export': True,
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        export_pickings = self.browse(cr, uid, ids, context=context)
        force_export = export_pickings and export_pickings[0].force_export or \
            False
        rows, picking_ids = self.get_data(cr, uid, ids,
                                          force_export=force_export,
                                          context=context)
        exporter = StockitExporter()
        data = exporter.get_csv_data(rows)
        if data:
            self.write(cr, uid, ids,
                       {'data': base64.encodestring(data),
                        'state': 'done'},
                       context=context)
            self.pool['stock.picking'].write(cr, uid, picking_ids,
                                                 {'stockit_export_date': str(
                                                     datetime.now())},
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

    def run_background_export(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if (not company.stockit_base_path or
                not company.stockit_in_picking_export):
            raise orm.except_orm(
                _('Error'),
                _('Stockit path is not configured on company.'))
        filename = "in_picking_export_with_id.csv"
        filepath = os.path.join(company.stockit_base_path,
                                company.stockit_in_picking_export,
                                filename)
        try:
            rows, picking_ids = self.get_data(cr, uid, [], force_export=False,
                                              context=context)
            exporter = StockitExporter(filepath)
            data = exporter.get_csv_data(rows)
            exporter.export_file(data)
            self.pool['stock.picking'].write(
                cr, uid, picking_ids,
                {'stockit_export_date': str(datetime.now())},
                context=context)
        except Exception as e:
            _logger.exception("Error exporting ingoing pickings file")
            message = _("Stock-it ingoing pickings failed "
                        "with error:<br>"
                        "%s") % e
            post_message(self, cr, uid, message, context=context)
        return True

    def get_data(self, cr, uid, ids, force_export=False, context=None):
        """Export incoming pickings in Stock iT format"""
        picking_obj = self.pool['stock.picking']
        context = context or {}
        context['lang'] = 'fr_FR'

        rows = []
        search_args = [('type', '=', 'in'), ('state', '=', 'assigned')]
        if not force_export:
            search_args.extend([('stockit_export_date', '=', False)])
        picking_ids = picking_obj.search(cr, uid, search_args, context=context)
        for picking in picking_obj.browse(cr, uid, picking_ids,
                                          context=context):
            address = picking.partner_id
            if address.parent_id:
                partner_name = address.parent_id.name
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
        return rows, picking_ids
