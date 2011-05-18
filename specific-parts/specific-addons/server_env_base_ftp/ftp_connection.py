# -*- coding: utf-8 -*-
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

from osv import fields, osv
from server_environment import serv_config


class FtpConnection(osv.osv):
    """ (S)FTP Connection"""
    _inherit = "ftp.connection"

    def _get_config(self, cr, uid, ids, field_names, arg, context):
        values = {}
        for ftp_conn in self.browse(cr, uid, ids, context):
            values[ftp_conn.id] = {}
            for field_name in field_names:
                section_name = '.'.join((self._name, ftp_conn.name))
                value = serv_config.get(section_name, field_name)
                values[ftp_conn.id].update({field_name: value})
        return values

    _columns = {
        'name': fields.char('Connection name', size=30, required=True, readonly=True),
        'server': fields.function(_get_config, type='char', size=256,
                    method=True, string='Server url', multi='config'),
        'remote_cwd': fields.function(_get_config, type='char', size=256,
                    method=True, string='Default remote repository',
                    multi='config'),
        'login': fields.function(_get_config, type='char', size=64,
                    method=True, string='Username', multi='config'),
        'password': fields.function(_get_config, type='char', size=64,
                    method=True, string='Password', multi='config'),
        'is_tls': fields.function(_get_config, type='boolean',
                    method=True, string='TLS?', multi='config'),
        'type': fields.function(_get_config, type='char',
                    method=True, string='Connection type', multi='config'),
        'local_cwd': fields.function(_get_config, type='char', size=256,
                    method=True, string='Default local repository',
                    multi='config'),
    }

FtpConnection()
