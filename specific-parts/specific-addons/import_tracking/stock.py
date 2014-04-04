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
import logging
import os
import shutil

from openerp.osv import orm
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)


class stock_picking(orm.Model):

    _inherit = 'stock.picking'

    def _update_tracking_references(self, cr, uid, packing_name,
                                    tracking_ref, context=None):
        """ Update the tracking reference of a packing
            tracking reference is updated only for packing (Outgoing Products)
            update only tracking references not already set
        """
        picking_ids = self.search(
            cr, uid,
            [('name', '=', packing_name),
             ('type', '=', 'out'),
             ('carrier_tracking_ref', '=', False),
             ('state', '=', 'done')],
            context=context)
        if picking_ids:
            self.write(cr, uid,
                       picking_ids,
                       {'carrier_tracking_ref': tracking_ref},
                       context=context)

    def import_tracking_references(self, cr, uid, ids, context=None):
        """ Read the Chronopost file and update
            the stock picking with the tracking reference
        """
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id

        path = company.tracking_csv_path_in
        if not path:
            return False
        if not os.path.exists(path):
            raise orm.except_orm(
                _('Error'),
                _('Path %s for the tracking numbers does not exist') % path)

        _logger.info('Started to import tracking number files')
        imported_files = []
        # read each file and each line in directory
        total = 0
        for root, __dirs, files in os.walk(path, topdown=False):
            for filename in files:
                total += 1
                filepath = os.path.join(root, filename)
                imported = self._import_tracking_from_file(
                    cr, uid, filepath, context=context)
                if imported:
                    imported_files.append(filename)

        # delete the file if all the tracking references have been
        # updated. only at end to not delete a file with after a
        # rollback
        for filename in imported_files:
            archive_path = os.path.join(path, 'archives')
            if not os.path.exists(archive_path):
                os.mkdir(archive_path)
            from_path = os.path.join(path, filename)
            to_path = os.path.join(archive_path, filename)
            shutil.move(from_path, to_path)
        _logger.info('Processed %s tracking files out of %s. %s files '
                     'with errors.', len(imported_files), total,
                     total - len(imported_files))
        return True

    def _import_tracking_from_file(self, cr, uid, filepath, context=None):
        _logger.info('Started to import tracking number file %s', filepath)
        with open(filepath, 'r') as trackfile:
            reader = csv.reader(trackfile, delimiter=';')

            for line in reader:
                if not line:  # handle empty lines
                    continue

                try:
                    tracking_ref = line[1].strip()
                    packing_name = line[6].strip()
                except IndexError:
                    _logger.exception("Tracking file %s could not be read at "
                                      "line %s. Import of file canceled.",
                                      filepath, line)
                    return
                if packing_name:
                    self._update_tracking_references(
                        cr, uid, packing_name, tracking_ref,
                        context=context)
            return True

    def run_import_tracking_references_scheduler(self, cr, uid, context=None):
        """ Scheduler for import tracking references """
        self.import_tracking_references(cr, uid, [], context=context)
        return True
