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
import paramiko

from osv import fields, osv
from tools.translate import _
from base_ftp.ftp_services.ftp import Service

class FtpConnection(osv.osv):
    """ (S)FTP Connection"""
    _name = "ftp.connection"
    _columns = {
        'name': fields.char('Connection name', size=30, required=True),
        'server': fields.char('Server url', size=256, required=True),
        'port': fields.integer('Port'),
        'remote_cwd': fields.char('Default remote repository', size=256),
        'login': fields.char('Username', size=64, required=True),
        'password': fields.char('Password', size=64),
        'is_tls': fields.boolean('TLS?'),
        'type': fields.selection((('ftp', 'FTP'),('sftp', 'SFTP')), 'Connection type' ,required=True),
        'local_cwd': fields.char('Default local repository', size=256),
    }

    def connect(self, cr, uid, id, context=None):
        if not context:
            context = {}

        ftp_conf = self.browse(cr, uid, id, context)
        ftp = Service(ftp_conf.type,
                      ftp_conf.server,
                      port=ftp_conf.port,
                      login=ftp_conf.login,
                      password=ftp_conf.password,
                      remote_cwd=ftp_conf.remote_cwd,
                      local_cwd=ftp_conf.local_cwd,
                      is_tls=ftp_conf.is_tls,)
        return ftp

FtpConnection()
