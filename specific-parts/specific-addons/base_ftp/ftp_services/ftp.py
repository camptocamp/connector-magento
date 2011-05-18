# -*- encoding: utf-8 -*-
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

import ftplib
import paramiko
import mimetypes


class ServiceAbstract(object):
    def __init__(self, connection_type, server, port=None, login=None,
                 password=None, remote_cwd=None, local_cwd=None,
                 *args, **kwargs):
        self.connection_type = connection_type
        self.server = server
        self.remote_cwd = remote_cwd
        self.local_cwd = local_cwd
        self.conn = None  # ftp object
        self.set_port(port)
        self.init_transport(server, port, **kwargs)
        import pdb; pdb.set_trace()
        self.login(login, password)
        self.set_remote_cwd(remote_cwd)

    def set_port(self, port=None):
        self.port = port

    def init_transport(self, server, port, **kwargs):
        raise NotImplementedError

    def login(self, login, password, **kwargs):
        raise NotImplementedError

    def set_remote_cwd(self, remote_cwd):
        raise NotImplementedError

    def mkdir(self, dir_name):
        raise NotImplementedError

    def push(self, local_path, remote_path):
        raise NotImplementedError

    def get(self, local_path, remote_path):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class FTPService(ServiceAbstract):
    @classmethod
    def is_class_for(cls, connection_type):
        return connection_type == 'ftp'

    def set_port(self, port):
        super(FTPService, self).set_port(port)
        if not self.port:
            self.port = 21

    def init_transport(self, server, port, **kwargs):
        if 'is_tls' in kwargs.keys() and kwargs['is_tls']:
            self.conn = ftplib.FTP_TLS()
        else:
            self.conn = ftplib.FTP()
        return self.conn.connect(self.server, self.port, **kwargs)

    def login(self, login, password, *kwargs):
        if not login:
            login = 'anonymous'
            if not password:
                password = 'anonymous@'
        import pdb; pdb.set_trace()
        return self.conn.login(login, password, *kwargs)

    def set_remote_cwd(self, remote_cwd):
        return self.conn.cwd(remote_cwd)

    def mkdir(self, dir_name):
        return self.conn.mkdir(dir_name)

    def push_binary(self, local_path, remote_path):
        filehandle = open(local_path, "rb")
        return self.conn.storbinary("STOR " + remote_path, filehandle)

    def push_text(self, local_path, remote_path):
        filehandle = open(local_path)
        return ftp.storlines("STOR " + remote_path, filehandle)

    def push(self, local_path, remote_path):
        mime = mimetypes.guess_type(local_path)[0]
        text = False
        if not mime:
            text = True
        if mime[0:5] == 'text/':
            text = True
        if text:
            return self.push_text(local_path, remote_path)
        else:
            return self.push_binary(local_path, remote_path)

    def get_text(self, local_path, remote_path):
        # fetch a text file
        if local_path is None:
            raise Exception("No local destination where to get the file")
        # use a lambda to add newlines to the lines read from the server
        return self.conn.retrlines("RETR " + remote_path, lambda s, w=local_path.write: w(s+"\n"))

    def get(self, local_path, remote_path):
        # only text mode support for now
        return self.get_text(local_path, remote_path)

    def close(self):
        self.conn.close()


class SFTPService(ServiceAbstract):
    @classmethod
    def is_class_for(cls, connection_type):
        return connection_type == 'sftp'

    def set_port(self, port):
        super(SFTPService, self).set_port(port)
        if not self.port:
            self.port = 22

    def init_transport(self, server, port, **kwargs):
        self.transport = paramiko.Transport((self.server, self.port))
        return True

    def login(self, login, password, **kwargs):
        self.transport.connect(username=login,
                               password=password)
        self.conn = paramiko.SFTPClient.from_transport(self.transport)
        return True

    def set_remote_cwd(self, remote_cwd):
        return self.conn.chdir(remote_cwd)

    def mkdir(self, dir_name):
        return self.conn.mkd(dir_name)

    def push(self, local_path, remote_path):
        return self.conn.put(local_path, remote_path)

    def get(self, local_path, remote_path):
        return self.conn.get(local_path, remote_path)

    def close(self):
        self.conn.close()
        

def Service(connection_type, *args, **kwargs):
    for cls in ServiceAbstract.__subclasses__():
        if cls.is_class_for(connection_type):
            return cls(connection_type, *args, **kwargs)
        raise ValueError
