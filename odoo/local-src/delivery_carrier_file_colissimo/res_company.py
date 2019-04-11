# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Charline Dumontet
#    Copyright 2017 Camptocamp SA
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
        'colissimo_file_path_in': fields.char(
            'Path for Colissimo tracking number files',
            help='Absolute path where the .txt files will be read to '
                 'update the tracking reference.'),
        'colissimo_archive_path': fields.char(
            'Colissimo archives path'),
        'colissimo_error_path': fields.char(
            'Colissimo errors path'),
    }

    def _check_colissimo_in_path(self, cr, uid, ids):
        for company in self.browse(cr, uid, ids):
            if not company.colissimo_file_path_in:
                continue
            if not os.path.exists(company.colissimo_file_path_in):
                return False
        return True

    _constraints = [
        (_check_colissimo_in_path,
         'Error: the path for tracking number files does not exist.',
         ['colissimo_file_path_in'])]
