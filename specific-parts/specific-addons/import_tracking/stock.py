# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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
##############################################################################

import base64
import csv
import os

from openerp.osv import orm


class stock_picking(orm.Model):

    _inherit = 'stock.picking'

    def _update_tracking_references(self, cr, uid, packing_name,
                                    tracking_ref, context=None):
        """ Update the tracking reference of a packing
            tracking reference is updated only for packing (Outgoing Products)
            update only tracking references not already set
        """
        found_packing = self.search(
            cr, uid,
            [('name', '=', packing_name),
             ('type', '=', 'out'),
             ('carrier_tracking_ref', '=', False),
             ('state', '=', 'done')],
            context=context)
        packing = self.browse(cr, uid, found_packing, context=context)
        if packing:
            self.write(cr, uid,
                       packing[0].id,
                       {'carrier_tracking_ref': tracking_ref},
                       context=context)
        return True

    def import_tracking_references(self, cr, uid, ids, context=None):
        """ Read the Chronopost file and update
            the stock picking with the tracking reference
        """
        attachment_obj = self.pool['ir.attachment']
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id

        directory = company.tracking_directory_id
        if not directory:
            return False

        for doc_file in directory.file_ids:
            decoded_data = base64.b64decode(doc_file.datas)
            reader = csv.reader(decoded_data.split(os.linesep), delimiter=';')

            updated = False
            for line in reader:
                if not line:  # handle empty lines
                    continue

                tracking_ref = line[1].strip()
                packing_name = line[6].strip()
                if packing_name:
                    updated = self._update_tracking_references(
                        cr, uid, packing_name, tracking_ref, context=context)

            if updated:
                attachment_obj.unlink(cr, uid, [doc_file.id], context=context)
        return True

    def run_import_tracking_references_scheduler(self, cr, uid, context=None):
        """ Scheduler for import tracking references """
        self.import_tracking_references(cr, uid, [], context=context)
        return True
