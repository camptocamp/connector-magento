# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu dietrich (Camptocamp)
#    Copyright 2015 Camptocamp SA
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
from openerp.osv import orm
from openerp import pooler
from openerp.tools.translate import _
from contextlib import closing
import psycopg2
import ftplib
import socket
import csv
import time
from datetime import datetime
from StringIO import StringIO
import re

import logging
_logger = logging.getLogger(__name__)


class EdiImportTracking(orm.Model):
    _name = "edi.import.tracking"

    def create_error_claim(self, cr, uid, error_message, context=None):
        __, section_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'stockit_synchro', 'section_stockit_error')
        __, categ_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'debonix_purchase_edi', 'categ_claim_pln_incident')
        claim_vals = {'name': _('PLN tracking import error'),
                      'description': error_message,
                      'categ_id': categ_id,
                      'section_id': section_id,
                      'claim_type': 'other'}
        self.pool['crm.claim'].create(cr, uid, claim_vals, context=context)

    def import_csv_tracking(self, cr, uid, ids=None, context=None):
        purchase_obj = self.pool['purchase.order']
        picking_obj = self.pool['stock.picking.out']

        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        host = company.edifact_host
        ftpuser = company.edifact_user
        ftppass = company.edifact_password
        importpath = company.edifact_purchase_import_path
        successpath = company.edifact_purchase_success_path
        errorpath = company.edifact_purchase_error_path
        import_file = company.edifact_purchase_import_file

        ftp = None
        try:
            res = {}
            # Connect to FTP
            ftp = ftplib.FTP(host, ftpuser, ftppass)
            ftp.cwd(importpath)
            pattern = re.compile(import_file)
            for filename in ftp.nlst():
                if pattern.match(filename):
                    data = StringIO()
                    ftp.retrbinary('RETR ' + filename, data.write)

                    # Go back at the start of the StringIO and read as CSV
                    data.seek(0)
                    csv_data = csv.reader(data, delimiter='|', quotechar='"')
                    for row in csv_data:
                        po_number = row[3]
                        date_done = datetime.strptime(row[2], "%Y/%m/%d "
                                                              "%H:%M:%S.%f")
                        tracking_ref = row[6].strip() and row[6] or row[0]
                        if (po_number not in res or
                                'carrier_tracking_ref' not in res[po_number]):
                            res[po_number] = {'carrier_tracking_ref': tracking_ref,
                                              'date_done': date_done}
                        else:
                            res[po_number]['carrier_tracking_ref'] += ";"
                            res[po_number]['carrier_tracking_ref'] += tracking_ref

                    # Write number in pickings + approve them
                    with closing(pooler.get_db(cr.dbname).cursor()) as new_cr:
                        error_message = ""
                        for po_number in res:
                            retries = 1
                            while retries <= 5:
                                try:
                                    po_ids = purchase_obj.search(
                                        new_cr, uid, [('name', '=', po_number)],
                                        context=context)
                                    picking_ids = picking_obj.search(
                                        new_cr, uid, [('purchase_id', 'in',
                                                       po_ids),
                                                      ('carrier_tracking_ref',
                                                       '=', False)],
                                        context=context)
                                    picking_obj.write(
                                        new_cr, uid, picking_ids, res[po_number],
                                        context=context)
                                    # Validate picking
                                    picking_obj.action_move(
                                        new_cr, uid, picking_ids, context=context)
                                    new_cr.commit()
                                    _logger.warning("SOGEDESCA PO %s validated",
                                                    po_number)
                                    break
                                except psycopg2.OperationalError:
                                    _logger.warning("Failed to validate picking "
                                                    "for SOGEDESCA PO %s: retry "
                                                    "%s/5",
                                                    po_number, retries,
                                                    exc_info=True)
                                    retries = retries + 1
                                    new_cr.rollback()
                                    time.sleep(2)
                            if retries == 5:
                                error_message += "PO %s not imported correctly " \
                                                 "from filename %s\n" \
                                                 % (po_number, filename)

                    # Move file to error or success folder
                    old_filename = filename
                    if error_message:
                        self.create_error_claim(cr, uid, error_message,
                                                context=context)
                        new_filename = errorpath + "/" + filename
                    else:
                        new_filename = successpath + "/" + filename
                    ftp.rename(old_filename, new_filename)

        except (socket.error, IOError) as err:
            raise Warning("Could not retrieve tracking file on FTP server: %s"
                          % err.message)
        finally:
            # Test for variable, None if connection failed
            if ftp:
                ftp.close()
        return True

