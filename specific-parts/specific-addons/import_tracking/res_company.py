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

import os

from openerp.osv import orm, fields


class res_company(orm.Model):

    _inherit = 'res.company'

    _columns = {
        'tracking_csv_path_in': fields.char(
            'Path for tracking number files',
            help='Absolute path where the CSV files will be read to '
                 'update the tracking reference.'),
    }

    def _check_tracking_csv_path(self, cr, uid, ids):
        for company in self.browse(cr, uid, ids):
            if not company.tracking_csv_path_in:
                continue
            if not os.path.exists(company.tracking_csv_path_in):
                return False
        return True

    _constraints = [
        (_check_tracking_csv_path,
         'Error: the path for tracking number files does not exist.',
         ['tracking_csv_path_in'])]
