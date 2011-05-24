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

import base64
from osv import osv, fields
from tools.translate import _
from stockit_synchro.stockit_exporter.exporter import StockitExporter


class StockItOutPickingExport(osv.osv_memory):
    _name = 'stockit.export.out.picking'
    _description = 'Export outgoing pickings in Stock iT format'

    _columns = {
        'filename': fields.char('Filename', 256, readonly=True),
    }

    def export(self, cr, uid, ids, context=None):
        """Export outgoing pickings in Stock iT format"""
        picking_obj = self.pool.get('stock.picking')
        context['lang'] = 'fr_FR'

        priority_mapping = {'1': 'BASSE', '2': 'NORMALE', '3': 'HAUTE'}

        rows = []
        picking_ids = picking_obj.search(cr, uid,
                                         [('type', '=', 'out'),
                                          ('state', '=', 'confirmed')],  # FIXME: check
                                         context=context)
        for picking in picking_obj.browse(cr, uid, picking_ids):
            for line in picking.move_lines:
                row = [
                    'S',  # type
                    picking.name,  # ref/name
                    line.date_planned,  # expected date
                    line.product_id.default_code,  # product code
                    str(line.product_qty),  # quantity
                    picking.priority and
                    priority_mapping[picking.priority] or
                    picking.priority['2'],  # priority
                ]
                rows.append(row)

        self.write_file(cr, uid, ids, rows, context)
        return True

    def write_file(self, cr, uid, ids, data, context=None):
        filename = '/tmp/out_picking_export.csv'  # TODO: set a filename: manual / generated filename ?
        exporter = StockitExporter(filename)
        exporter.export_file(data)
        result = self.write(cr,
                            uid,
                            ids,
                            {'filename': filename, },
                            context=context)
        return result

StockItOutPickingExport()
