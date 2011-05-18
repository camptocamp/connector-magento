# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi & Guewen Baconnier. Copyright Camptocamp SA
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

import ftplib

from osv import fields, osv
from tools.translate import _


class ResCompany(osv.osv):
    """override company to add ftp config for stock it"""
    _inherit = "res.company"

    _columns = {
        'stockit_ftp_connection': fields.many2one('ftp.connection','FTP Connection for Stock iT synchronisations')
    }

ResCompany()
