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
from datetime import datetime
import base64

import netsvc
import wizard
import pooler

from osv import osv, fields
from tools.translate import _
from stockit_synchro.stockit_exporter.exporter import StockitExporter


class StockItOutPickingExport(osv.osv_memory):
    _name = 'stockit.export.out.picking'
    _description = 'Export outgoing pickings in Stock iT format'

    _columns = {
        'data': fields.binary('File', readonly=True),
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        rows = self.get_data(cr, uid, [], context)
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
        filename = "out_picking_export_with_id.csv"
        filepath = os.path.join(company.stockit_base_path,
                                company.stockit_out_picking_export,
                                filename)
        db, pool = pooler.get_db_and_pool(cr.dbname)
        mycursor = db.cursor()
        try:
            rows = self.get_data(mycursor, uid, [], context)
            exporter = StockitExporter(filepath)
            data = exporter.get_csv_data(rows)
            exporter.export_file(data)
        except Exception, e:
            mycursor.rollback()
            self.create_request_error(cr, uid, str(e), context)
        finally:
            mycursor.commit()
            mycursor.close()
        return True

    def get_data(self, cr, uid, ids, context=None):
        """Export outgoing pickings in Stock iT format"""
        picking_obj = self.pool.get('stock.picking')
        context = context or {}
        context['lang'] = 'fr_FR'

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_out_pick_exp_location_id:
            raise osv.except_osv(_('Error'), _('Location to export is not configured on the company.'))

        only_from_location = company.stockit_out_pick_exp_location_id

        priority_mapping = {'1': 'BASSE', '2': 'NORMALE', '3': 'HAUTE', '9': 'SHOP'}
        rows = []

        search =  [('type', '=', 'out'),
                   ('state', '=', 'assigned'),
        ]
        if ids:
            search.append(('id', 'in', ids))
        picking_ids = picking_obj.search(cr,
                                         uid,
                                         search,
                                         context=context)
        # we look for outdated
        search = [('type', '=', 'out'),
                  ('stockit_outdated', '=', True),
                  ('state', '=', 'cancel')]
        if ids:
            search.append(('id', 'in', ids))
        picking_ids += picking_obj.search(cr,
                                          uid,
                                          search,
                                          context=context)
        picking_ids = list(set(picking_ids))
        for picking in picking_obj.browse(cr, uid, picking_ids):
            if picking.state == 'cancel':
                row=['S',  # type
                     str(picking.id),  # unique id
                     picking.name,  # ref/name
                     '',  # expected date
                     '',  # product code
                     0.0,  # quantity
                     '']  # priority
                rows.append(row)
            else:
                for line in picking.move_lines:
                    if line.product_id.type == 'service':
                        continue  # skip service products
                    if only_from_location and line.location_id.id != only_from_location.id:
                        continue  # skip line if stock location is not the one to export
                    qty = line.state != 'cancel' and line.product_qty or 0.0
                    row = ['S',  # type
                           str(picking.id),  # unique id
                           picking.name,  # ref/name
                           line.date_planned,  # expected date
                           line.product_id.default_code,  # product code
                           str(qty),  # quantity
                           picking.priority and
                           priority_mapping[picking.priority] or
                           picking.priority['2'],]  # priority
                    rows.append(row)
            picking_obj.write(cr,
                              uid,
                              [picking.id],
                              {'stockit_export_date': str(datetime.now()),
                               'stockit_outdated': False})
        return rows

StockItOutPickingExport()

## We make a wizard as the customer want to be able to export directly selected
## picking into list form mode.
## in V5 active_ids support does not work well We do a wizard to be ported in next migration to V6.x.x
## this wizard shoul inherit StockItOutPickingExport

FORM = """<?xml version="1.0"?>
<form string="Stockit export">
<separator string="Export selected picking to stockit. File will be automatically put in stockit folder"/>
</form>
"""
FIELDS = {}

FORM1 = """<?xml version="1.0"?>
<form string="Stockit exported file">
<separator colspan="4" string="Clic on 'Save as' to save the CSV file :" />
    <field name="export"/>
</form>
"""
FIELDS1 = {'export':
           {'string': 'stockit file',
            'type': 'binary',
            'readonly': True,}}


def _compute_export(self, cr, uid, data, context):
    ids = data['ids']
    if not ids:
        raise wizard.except_wizard(_('Impossible Action'),
                                   _('No picking selected'))
    if ids and not isinstance(ids, list):
        ids = [ids]
    self.pool = pooler.get_pool(cr.dbname)
    exp_obj = self.pool.get('stockit.export.out.picking')
    user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
    company = user.company_id
    if not company.stockit_base_path or not company.stockit_out_picking_export:
        raise wizard.except_wizard(_('Error'),
                                   _('Stockit path is not configured on company.'))

    filename = "out_picking_export_with_id_%s.csv" % (datetime.now().isoformat().replace(':','_'),)
    filepath = os.path.join(company.stockit_base_path,
                           company.stockit_out_picking_export,
                           filename)
    rows = exp_obj.get_data(cr, uid, ids, context)
    if not rows:
        raise wizard.except_wizard(_('No row exported'),
                                   _('Only out and assigned rows will be exported'
                                     ' or exported once and canceled'))
    try:
        exporter = StockitExporter(filepath)
        data = exporter.get_csv_data(rows)
        exporter.export_file(data)
    except Exception, e:
        raise wizard.except_wizard(_('Stockit export'), str(e))

    return {'export': base64.encodestring(data)}



class SelectedOutPickExporter(wizard.interface):
    
    
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                'arch' : FORM,
                'fields' : FIELDS,
                'state' : [('end','Cancel'),('export', 'OK')]
            }
        },
        'export' : {
            'actions' : [_compute_export],
            'result' : {'type' : 'form',
                'arch' : FORM1,
                'fields' : FIELDS1,
                'state' : [('end', 'OK', 'gtk-ok', True)]
            }
        }
    }

SelectedOutPickExporter('stockit.export.selected')
