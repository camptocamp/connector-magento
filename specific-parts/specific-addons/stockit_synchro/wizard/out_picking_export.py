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
import logging
import os

from datetime import datetime

from openerp import pooler

from openerp.osv import orm, fields
from openerp.tools.translate import _
from ..stockit_exporter.exporter import StockitExporter


_logger = logging.getLogger(__name__)


class StockItOutPickingExport(orm.TransientModel):
    _name = 'stockit.export.out.picking'
    _description = 'Export outgoing pickings in Stock iT format'

    _columns = {
        'data': fields.binary('File', readonly=True),
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        rows = self._get_data(cr, uid, [], context=context)
        exporter = StockitExporter()
        data = exporter.get_csv_data(rows)
        result = self.write(cr,
                            uid,
                            ids,
                            {'data': base64.encodestring(data)},
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
        _logger.error("Error exporting outgoing pickings file: %s", err_msg)

        # TODO post a message
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

    def background_export(self, cr, uid, picking_ids, only_new=True, context=None):
        """
        Export the pickings in background and store them in a file
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if (not company.stockit_base_path or not
                company.stockit_out_picking_export):
            raise orm.except_orm(
                _('Error'),
                _('Stockit path is not configured on company.'))
        filename = "out_picking_export_with_id_%s.csv" % \
            (datetime.now().isoformat().replace(':', '_'),)
        filepath = os.path.join(company.stockit_base_path,
                                company.stockit_out_picking_export,
                                filename)
        db, pool = pooler.get_db_and_pool(cr.dbname)
        mycursor = db.cursor()
        data = False
        try:
            rows = self._get_data(
                mycursor, uid, picking_ids, only_new=only_new, context=context)
            exporter = StockitExporter(filepath)
            data = exporter.get_csv_data(rows)
            exporter.export_file(data)
        except Exception as e:
            mycursor.rollback()
            self.create_request_error(cr, uid, str(e), context)
            raise
        finally:
            mycursor.commit()
            mycursor.close()
        return data

    def run_background_export(self, cr, uid, context=None):
        """ export all packings, according to filters, in background"""
        return self.background_export(cr, uid, [], context=context)

    def _get_data(self, cr, uid, picking_ids=None, only_new=True, context=None):
        """Export outgoing pickings in Stock iT format
        When no picking_ids are provided,
        it means that the normal, auto mode (cron)
        otherwise, that's the manuel mode and we export only
        what has been selected on the manual wizard
        (excluding the ones which are outside of the domain)"""
        picking_obj = self.pool.get('stock.picking')
        context = context or {}
        context['lang'] = 'fr_FR'

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_out_pick_exp_location_id:
            raise orm.except_orm(
                _('Error'),
                _('Stock Location to export is not configured on the company.'))

        only_from_location = company.stockit_out_pick_exp_location_id

        priority_mapping = {'0': 'BASSE', '1': 'NORMALE', '2': 'HAUTE', '9': 'SHOP'}
        rows = []

        force_pickings = False
        domain = [('type', '=', 'out'),
                  ('state', '=', 'assigned')]
        if picking_ids:
            force_pickings = True
            domain.append(('id', 'in', picking_ids))
        picking_ids = picking_obj.search(
            cr, uid, domain, context=context)

        if only_new:
            # use a cr.execute query because
            # we cannot compare 2 fields using orm search
            query = ("SELECT id "
                     "FROM   stock_picking "
                     "WHERE  id in %s "
                     "AND (stockit_export_date ISNULL "
                     "     OR write_date > stockit_export_date)")
            cr.execute(query, (tuple(picking_ids), ))

            picking_ids = [pick_id[0] for pick_id in cr.fetchall()]

        # when we force picking ids we do want only those one
        if not force_pickings:
            # we look for outdated
            search = [('type', '=', 'out'),
                      ('stockit_outdated', '=', True),
                      ('state', '=', 'cancel'), ]

            picking_ids += picking_obj.search(cr,
                                              uid,
                                              search,
                                              context=context)

        picking_ids = list(set(picking_ids))
        for picking in picking_obj.browse(cr, uid, picking_ids, context=context):
            name = picking.name
            if picking.state == 'cancel':
                row = ['S',  # type
                       str(picking.id),  # unique id
                       name[:18],  # ref/name
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
                    priority = (priority_mapping[picking.priority]
                                if picking.priority else picking.priority['1'])
                    row = ['S',  # type
                           str(picking.id),  # unique id
                           name[:18],  # ref/name
                           line.date,  # scheduled date / move date
                           line.product_id.default_code,  # product code
                           str(qty),  # quantity
                           priority]
                    rows.append(row)
            picking_obj.write(cr,
                              uid,
                              [picking.id],
                              {'stockit_export_date': str(datetime.now()),
                               'stockit_outdated': False})
        return rows


class StockItOutPickingManualExport(orm.TransientModel):
    """Export the selected outgoing packings directly
    in the configured path
    """

    _name = 'stockit.manual.export.out.picking'
    _description = 'Export selected outgoing pickings'

    def _get_picking_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = False
        if (context.get('active_model') == 'stock.picking' and
            context.get('active_ids')):
            res = context['active_ids']
        return res

    _columns = {
        'picking_ids':
            fields.many2many(
                'stock.picking',
                string='Delivery Orders',
                domain=[('type', '=', 'out'), ('state', '=', 'assigned')]),
        'only_new': fields.boolean('Only not yet exported'),
        'data': fields.binary('File', readonly=True),
    }

    _defaults = {
        'only_new': True,
        'picking_ids': _get_picking_ids,
    }

    def export(self, cr, uid, ids, context=None):
        form = self.browse(cr, uid, ids[0], context=context)

        picking_ids = [p.id for p in form.picking_ids]
        exp_obj = self.pool.get('stockit.export.out.picking')
        data = exp_obj.background_export(
            cr, uid, picking_ids, only_new=form.only_new, context=context)

        if not data:
            raise orm.except_orm(_('Error'), _('Nothing has been exported'))

        self.write(cr, uid, form.id, {'data': base64.encodestring(data)})

        return True
