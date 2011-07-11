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

import datetime
import os
import glob
import netsvc

from osv import osv, fields
from tools.translate import _
from operator import itemgetter
from itertools import groupby
from stockit_synchro.stockit_importer.importer import StockitImporter


class StockItInPickingImport(osv.osv_memory):
    _name = 'stockit.import.in.picking'
    _description = 'Import incoming pickings in Stock iT format'

    _columns = {
        'data': fields.binary('File', required=True),
        'filename': fields.char('Filename', size=256,
                                required=True, readonly=False),
    }

    def import_in_picking(self, cr, uid, ids, context=None):
        """ Import incoming pickings according to the Stock it file
        and returns the updated picking ids
        """
        if isinstance(ids, list):
            ids = ids[0]

        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        stock_move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")

        wizard = self.browse(cr, uid, ids, context)
        if not wizard.data:
            raise osv.except_osv(_('UserError'),
                                 _("You need to select a file!"))

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        default_location_id = company.stockit_in_picking_location_id
        default_location_dest_id = company.stockit_in_picking_location_dest_id

        # header to apply on the csv file (no header on the file)
        # in the right order
        header = ['type', 'id', 'picking_name', 'planned_date', 'default_code',
                  'brand', 'expected_qty', 'received_qty', 'ean', 'width',
                  'length', 'height', 'picking_capacity', ]

        conversion_types = {
            'type': unicode,
            'id': int,
            'picking_name': unicode,
            'planned_date': datetime.datetime,
            'default_code': unicode,
            'brand': unicode,
            'expected_qty': float,
            'received_qty': float,
            'ean': unicode,
            'width': float,
            'length': float,
            'height': float,
            'picking_capacity': float,
        }

        importer = StockitImporter()
        importer.read_from_base64(wizard.data)
        rows = importer.csv_to_dict(header)
        rows = importer.cast_rows(rows, conversion_types)

        # E means incoming product for stockit
        rows = [row for row in rows if row['type'] == 'E']

        # create ean on product if it does not already exist
        product_ean_list = {}
        for row in rows:
            product_ids = product_obj.search(cr, uid,
                [('default_code', '=', row['default_code'])])
            if not product_ids:
                raise Exception('ImportError', "Product %s not found !" %
                                               (row['default_code'],))
            product_id = product_ids[0]
            if product_id not in product_ean_list.keys():
                product_ean_list[product_id] = []
            product_ean_list[product_id].append(row['ean'])

        for product_id in product_ean_list:
            product_obj.add_ean_if_not_exists(cr, uid,
                                              product_id,
                                              product_ean_list[product_id],
                                              context)

        # sum quantities of duplicate products in a packing and remove them
        rows = sorted(rows, key=itemgetter('id', 'default_code'))
        if rows:
            last = rows[-1]
            for index in range(len(rows) - 2, -1, -1):
                if last['id'] == rows[index]['id'] and \
                   last['default_code'] == rows[index]['default_code']:
                    last['expected_qty'] = last['expected_qty'] + \
                                       rows[index]['expected_qty']
                    last['received_qty'] = last['received_qty'] + \
                                       rows[index]['received_qty']
                    del rows[index]
                else:
                    last = rows[index]

        imported_picking_ids = []

        for picking_id, rows in groupby(rows,
                                          lambda row: row['id']):
            picking_ids = picking_obj.search(cr, uid,
                [('id', '=', picking_id)])

            if not picking_ids:
                raise osv.except_osv(_('ImportError'), _("Picking %s not found !") %
                                               (picking_id,))
            picking_id = picking_ids[0]
            picking = picking_obj.browse(cr, uid, picking_id)

            if picking.state in ('stockit_confirm', 'done'):
                continue  # already imported

            not_receipt_moves = {}
            for move in picking.move_lines:
                not_receipt_moves[move.product_id.id] = move

            complete, too_many, too_few, new_moves = [], [], [], []
            for row in rows:
                product_ids = product_obj.search(cr, uid,
                                                 [('default_code', '=',
                                                   row['default_code'])])
                if not product_ids:
                    raise osv.except_osv(_('ImportError'), _("Product %s not found !") %
                                                   (row['default_code'],))
                product_id = product_ids[0]

                found_product = False
                for move in picking.move_lines:
                    if move.product_id.id == product_id:
                        del(not_receipt_moves[product_id])
                        found_product = True

                        backorder_move = {'move': move,
                                          'qty': row['received_qty']}

                        if move.product_qty == row['received_qty']:
                            complete.append(backorder_move)
                        elif move.product_qty > row['received_qty']:
                            too_few.append(backorder_move)
                        else:
                            too_many.append(backorder_move)
                        break

                # new product in the picking
                if not found_product:
                    stock_move_values = stock_move_obj.onchange_product_id(
                        cr, uid, [],
                        prod_id=product_id,
                        loc_id=default_location_id.id,
                        loc_dest_id=default_location_dest_id.id,
                        address_id=picking.address_id.id
                    )['value']

                    stock_move_values.update({
                        'picking_name': row['picking_name'],
                        'product_id': product_id,
                        'product_qty': row['received_qty']
                    })
                    new_moves.append(stock_move_values)

            for product_id, move in not_receipt_moves.iteritems():
                backorder_move = {'move': move, 'qty': 0.0}
                too_few.append(backorder_move)

            backorder_id = self._create_backorder(cr, uid, picking.id, complete,
                                                  too_many, too_few, new_moves,
                                                  context=context)

            picking_obj.write(cr, uid, backorder_id, {'state': 'stockit_confirm'})
            wf_service.trg_write(uid, 'stock.picking', backorder_id, cr)
            imported_picking_ids.append(backorder_id)

        return imported_picking_ids

    def _create_backorder(self, cr, uid, picking_id, complete, too_many,
                          too_few, new_moves, context=None):
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        new_picking = None

        picking = pick_obj.browse(cr, uid, picking_id)

        if too_few or new_moves:
            # create a backorder
            new_picking = pick_obj.copy(cr, uid, picking.id,
                    {
                        'name': self.pool.get('ir.sequence').\
                                 get(cr, uid, 'stock.picking'),
                        'move_lines': [],
                        'state': 'draft',
                    })

        for move_dict in too_few:
            move = move_dict['move']
            qty = move_dict['qty']
            if qty:
                move_obj.copy(cr, uid, move.id,
                    {
                        'product_qty': qty,
                        'product_uos_qty': qty,
                        'picking_id': new_picking,
                        'state': 'assigned',
                        'move_dest_id': False,
                        'price_unit': move.price_unit,
                    })
            move_obj.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty - qty,
                        'product_uos_qty': move.product_qty - qty,
                    })

        for move in new_moves:
            move.update({'picking_id': new_picking})
            move_id = move_obj.create(cr, uid, move)
            move_obj.force_assign(cr, uid, move_id)

        if new_picking:
            # move complete moves to backorder
            move_obj.write(cr, uid, [c['move'].id for c in complete],
                    {'picking_id': new_picking})

            # update qty and move "too many" moves to backorder
            for move_dict in too_many:
                move_obj.write(cr, uid, [move_dict['move'].id],
                        {
                            'product_qty': move_dict['qty'],
                            'product_uos_qty': move_dict['qty'],
                            'picking_id': new_picking,
                        })
        else:
            for move_dict in too_many:
                move_obj.write(cr, uid, [move_dict['move'].id],
                        {
                            'product_qty': move_dict['qty'],
                            'product_uos_qty': move_dict['qty']
                        })

        # assign the backorder
        if new_picking:
            pick_obj.write(cr, uid, [picking.id], {'backorder_id': new_picking})

        wf_service = netsvc.LocalService("workflow")
        pick_obj.force_assign(cr, uid, [new_picking or picking.id])
        wf_service.trg_validate(uid, 'stock.picking',
                                 new_picking or picking.id, 'button_confirm', cr)

        return new_picking or picking.id

    def action_import(self, cr, uid, ids, context=None):
        """ Update incoming pickings according the Stock it file
        """

        imported_picking_ids = self.import_in_picking(cr, uid, ids, context)
        res = {'type': 'ir.actions.act_window_close'}
        if imported_picking_ids:
            model_obj = self.pool.get('ir.model.data')
            model_data_ids = model_obj.search(cr, uid, [
                            ('model', '=', 'ir.ui.view'),
                            ('module', '=', 'stock'),
                            ('name', '=', 'view_picking_in_form')
                        ])
            resource_id = model_obj.read(cr, uid,
                                         model_data_ids,
                                         fields=['res_id'],
                                         context=context)[0]['res_id']

            res = {
                'name': _("Incoming pickings imported from Stock-it"),
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(False, 'tree'), (resource_id, 'form')],
                'domain': "[('id', 'in', %s)]" % imported_picking_ids,
                'context': context,
            }
        return res

    def create_request_error(self, cr, uid, file, err_msg, context=None):
        logger = netsvc.Logger()
        logger.notifyChannel(
                             _("Stockit ingoing picking import"),
                             netsvc.LOG_ERROR,
                             _("Error importing ingoing picking file %s : %s" % (file, err_msg)))

        request = self.pool.get('res.request')
        summary = _("Stock-it ingoing picking import failed on file : %s\n"
                    "With error:\n"
                    "%s") % (file, err_msg)

        request.create(cr, uid,
                       {'name': _("Stock-it ingoing picking import"),
                        'act_from': uid,
                        'act_to': uid,
                        'body': summary,
                        })
        return True

    def run_background_import(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        if not company.stockit_base_path or not company.stockit_in_picking_import:
            raise osv.except_osv(_('Error'), _('Stockit path is not configured on company.'))

        files_folder = os.path.join(company.stockit_base_path,
                                    company.stockit_in_picking_import)
        files = glob.glob(os.path.join(files_folder, '*'))
        for file in files:
            imported_picking_ids = False
            data_file = open(file, 'r')
            try:
                data = data_file.read().encode("base64")
                wizard = self.create(cr, uid, {'data': data}, context=context)
                imported_picking_ids = self.import_in_picking(cr, uid, [wizard], context)
            except osv.except_osv, e:
                self.create_request_error(cr, uid, file, e.value, context)
            except Exception, e:
                self.create_request_error(cr, uid, file, str(e), context)
            finally:
                data_file.close()
            if imported_picking_ids:
                os.unlink(file)
        return True


StockItInPickingImport()
