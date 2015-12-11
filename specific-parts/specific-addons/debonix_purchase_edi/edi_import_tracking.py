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
import ftplib
import socket
import csv
from datetime import datetime
from StringIO import StringIO


class EdiImportTracking(orm.Model):
    _name = "edi.import.tracking"

    def import_csv_tracking(self, cr, uid, ids=None, context=None):
        purchase_obj = self.pool['purchase.order']
        picking_obj = self.pool['stock.picking.out']

        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        host = company.edifact_purchase_host
        ftpuser = company.edifact_purchase_user
        ftppass = company.edifact_purchase_password
        importpath = company.edifact_purchase_import_path
        import_file = company.edifact_purchase_import_file

        ftp = None
        try:
            res = {}
            # Connect to FTP
            ftp = ftplib.FTP(host, ftpuser, ftppass)
            ftp.cwd(importpath)
            # Retrieve today's file
            now = datetime.now().strftime('%Y%m%d')
            filename = import_file % (now,)
            data = StringIO()
            ftp.retrbinary('RETR ' + filename, data.write)

            # Go back at the start of the StringIO and read as CSV
            data.seek(0)
            csv_data = csv.reader(data, delimiter='|', quotechar='"')
            for row in csv_data:
                po_number = row[3]
                date_done = datetime.strptime(row[2], "%Y/%m/%d %H:%M:%S.%f")
                tracking_ref = row[6].strip() and row[6] or row[0]
                if (po_number not in res or
                        'carrier_tracking_ref' not in res[po_number]):
                    res[po_number] = {'carrier_tracking_ref': tracking_ref,
                                      'date_done': date_done}
                else:
                    res[po_number]['carrier_tracking_ref'] += ";"
                    res[po_number]['carrier_tracking_ref'] += tracking_ref

            # Write number in pickings + approve them
            for po_number in res:
                po_ids = purchase_obj.search(
                    cr, uid, [('name', '=', po_number)], context=context)
                picking_ids = picking_obj.search(
                    cr, uid, [('purchase_id', 'in', po_ids)], context=context)
                picking_obj.write(
                    cr, uid, picking_ids, res[po_number], context=context)
                # Validate picking
                picking_obj.action_move(
                    cr, uid, picking_ids, context=context)
        except (socket.error, IOError) as err:
            raise Warning("Could not retrieve tracking file on FTP server: %s"
                          % err.message)
        finally:
            # Test for variable, None if connection failed
            if ftp:
                ftp.close()
        return True

