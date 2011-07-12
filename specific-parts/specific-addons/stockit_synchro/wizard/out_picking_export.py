# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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

import os
import netsvc
import base64

from osv import osv, fields
from tools.translate import _
from datetime import datetime
from stockit_synchro.stockit_exporter.exporter import StockitExporter


class StockItOutPickingExport(osv.osv_memory):
    _name = 'stockit.export.out.picking'
    _description = 'Export outgoing pickings in Stock iT format'

    _columns = {
        'data': fields.binary('File', readonly=True),
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        rows = self.get_data(cr, uid, ids, context)
        exporter = StockitExporter()
        data = exporter.get_csv_data(rows)
        result = self.write(cr,
                            uid,
                            ids,
                            {'data': base64.encodestring(data)},
                            context=context)
        return result

    def create_request_error(self, cr, uid, err_msg, context=None):
        logger = netsvc.Logger()
        logger.notifyChannel(
                             _("Stockit Outgoing Picking Export"),
                             netsvc.LOG_ERROR,
                             _("Error exporting outgoing pickings file : %s" % (err_msg,)))

        request = self.pool.get('res.request')
        summary = _("Stock-it outgoing pickings failed\n"
                    "With error:\n"
                    "%s") % (err_msg,)

        request.create(cr, uid,
                       {'name': _("Stock-it outgoing pickings export"),
                        'act_from': uid,
                        'act_to': uid,
                        'body': summary,
                        })
        return True

    def run_background_export(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_base_path or not company.stockit_out_picking_export:
            raise osv.except_osv(_('Error'), _('Stockit path is not configured on company.'))
        now = datetime.now()
        filename = "out_picking_export_%i%i%i%i%i.csv" % (now.year, now.month, now.day, now.hour, now.minute)
        filepath = os.path.join(company.stockit_base_path,
                                company.stockit_out_picking_export,
                                filename)
        try:
            rows = self.get_data(cr, uid, [], context)
            exporter = StockitExporter(filepath)
            data = exporter.get_csv_data(rows)
            exporter.export_file(data)
        except Exception, e:
            self.create_request_error(cr, uid, str(e), context)
        return True

    def get_data(self, cr, uid, ids, context=None):
        """Export outgoing pickings in Stock iT format"""
        picking_obj = self.pool.get('stock.picking')
        context = context or {}
        context['lang'] = 'fr_FR'

        priority_mapping = {'1': 'BASSE', '2': 'NORMALE', '3': 'HAUTE'}

        rows = []
         # FIXME: check domain
        picking_ids = picking_obj.search(cr, uid,
                                         [('type', '=', 'out'),
                                          ('state', '=', 'confirmed')],
                                         context=context)
        for picking in picking_obj.browse(cr, uid, picking_ids):
            for line in picking.move_lines:
                row = [
                    'S',  # type
                    str(picking.id),  # unique id
                    picking.name,  # ref/name
                    line.date_planned,  # expected date
                    line.product_id.default_code,  # product code
                    str(line.product_qty),  # quantity
                    picking.priority and
                    priority_mapping[picking.priority] or
                    picking.priority['2'],  # priority
                ]
                rows.append(row)
        return rows

StockItOutPickingExport()
