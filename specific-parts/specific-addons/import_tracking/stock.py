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

from contextlib import closing

from openerp.osv import orm
from openerp import pooler
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)


class ImportError(Exception):
    pass


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

        archive_path = os.path.join(path, 'archives')
        if not os.path.exists(archive_path):
            os.mkdir(archive_path)

        _logger.info('Started to import tracking number files')
        imported_files = []
        # read each file and each line in directory
        total = 0
        db = pooler.get_db(cr.dbname)
        with closing(db.cursor()) as local_cr:
            for root, __dirs, files in os.walk(path, topdown=False):
                for filename in files:
                    try:
                        total += 1
                        filepath = os.path.join(root, filename)
                        imported = self._import_tracking_from_file(
                            local_cr, uid, filepath, context=context)
                    except Exception as err:
                        local_cr.rollback()
                        _logger.exception("Tracking file %s could not be imported", filepath)
                        message = (_("Tracking file %s could not be imported due to: %s") %
                                   (filepath, err))
                        self._post_import_tracking_error_message(
                            cr, uid, message, context=context)
                        continue
                    else:
                        if imported:
                            from_path = os.path.join(path, filename)
                            to_path = os.path.join(archive_path, filename)
                            shutil.move(from_path, to_path)
                            # commit so if next file fails we won't lose
                            # the imported trackings
                        local_cr.commit()

        _logger.info('Processed %s tracking files out of %s. %s files '
                     'with errors.', len(imported_files), total,
                     total - len(imported_files))
        return True

    def _post_import_tracking_error_message(self, cr, uid, message,
                                            subtype='mail.mt_comment',
                                            context=None):
        data_obj = self.pool['ir.model.data']
        mail_group_obj = self.pool['mail.group']
        try:
            __, mail_group_id = data_obj.get_object_reference(
                cr, uid, 'import_tracking', 'group_import_tracking')
            mail_group_obj.message_post(
                cr, uid, [mail_group_id],
                body=message,
                subtype=subtype,
                context=context)
        except ValueError:
            _logger.error('Could not post a notification about the error '
                          'because the Import Tracking group has been deleted')

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
                    message = ("Tracking file %s could not be read at "
                               "line %s. Import of file canceled.")
                    _logger.exception(message, filepath, line)
                    self._post_import_tracking_error_message(
                        cr, uid, _(message) % (filepath, line),
                        context=context)
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
