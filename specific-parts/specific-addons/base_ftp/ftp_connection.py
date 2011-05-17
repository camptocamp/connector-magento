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


class FtpConnection(osv.osv):
    """ (S)FTP Connection"""
    _name = "ftp.connection"
    _columns = {
        'name': fields.char('Connection name', size=30, required=True),
        'server': fields.char('Server url', size=256, required=True),
        'remote_cwd': fields.char('Default remote repository', size=256),
        'login': fields.char('Username', size=256, required=True),
        'password': fields.char('Password', size=256),
        'is_tsl': fields.boolean('TSL?'),
        'is_ssh': fields.boolean('SFTP?'),
        'local_cwd': fields.char('Default local repository', size=256),
    }

    def connect(self, cr, uid, id, context=None):
        if not context:
            context = {}

        ftp = None
        ftp_conn = self.browse(cr, uid, id, context)
        is_ssh = ftp_conn.is_ssh
        try:
            # TODO: port configuration
            if is_ssh:
                transport = paramiko.Transport((ftp_conn.server, 22))
                transport.connect(username=ftp_conn.login,
                                  password=ftp_conn.password)
                ftp = paramiko.SFTPClient.from_transport(transport)
                if ftp_conn.remote_cwd:
                    ftp.chdir(ftp_conn.remote_cwd)
            else:
                if ftp_conn.is_tsl:
                    ftp = ftplib.FTP_TLS(ftp_conn.server)
                else:
                    ftp = ftplib.FTP(ftp_conn.server)
                ftp.login(ftp_conn.login,
                          ftp_conn.password)
                if ftp_conn.remote_cwd:
                    ftp.cwd(ftp_conn.remote_cwd)
        except Exception, e:
            raise Exception(
                _('Could not establish connection with ftp/sftp server: ')
                + str(e))
        return ftp

FtpConnection()
