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
import datetime
from osv import osv, fields
from tools.translate import _
from stockit_synchro.file_parser.parser import FileParser


class StockItInPickingExport(osv.osv_memory):
    _name = 'stockit.export.in.picking'
    _description = 'Export ingoing pickings in Stock iT format'

    _columns = {
        'data': fields.binary('File', required=True),
        'filename': fields.char('Filename', size=256, required=True, readonly=False),
    }

    def get_from_ftp(self, cr, uid, ids, context=None):
        """ Connect on the ftp and copy the file locally
        """
        pass

    def action_import(self, cr, uid, ids, context=None):
        """ Update ingoing pickings according the Stock it file
        """
        context = context or {}
        if isinstance(ids, list):
            req_id = ids[0]
        picking_obj = self.pool.get('stock.picking')

        wizard = self.browse(cr, uid, req_id, context)
        if not wizard.data:
            raise osv.except_osv(_('UserError'), _("You need to select a file!"))

        types_dict = {
                            0: unicode,  # type (always RE)
                            1: unicode,  # picking name
                            2: datetime.datetime,  # planned date
                            3: unicode,  # product code
                            4: unicode,  # brand
                            5: float,  # expected quantity
                            6: float,  # received quantity
                            7: unicode,  # ean13 code
                            8: float,  # width
                            9: float,  # length
                            10: float,  # height
                            11: float,  # picking capacity
        }

        csv_parser = FileParser(wizard.data, decode_base_64=True, ftype='csv')
        lines = csv_parser.parse(delimiter='|')
        lines = csv_parser.cast_rows(lines, types_dict)

        imported_picking_ids = []
        pickings = {}
        for line in lines:
            if line[1] in pickings.keys():
                pickings[line[1]].append(line)
            else:
                pickings[line[1]] = [line]

        for picking in pickings:
            pass

        model_obj  = self.pool.get('ir.model.data')
        model_data_ids = model_obj.search(cr, uid, [
                        ('model','=','ir.ui.view'),
                        ('module','=','stock'),
                        ('name','=','view_picking_in_tree')
                    ])
        resource_id = model_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        
        res =  {
            'name': _("Imported ingoing pickings"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(False,'tree'), (resource_id,'form')],
            'domain': "[('id', 'in', %s)]" % imported_picking_ids,
            'context': context,
        }
        return res

StockItInPickingExport()
