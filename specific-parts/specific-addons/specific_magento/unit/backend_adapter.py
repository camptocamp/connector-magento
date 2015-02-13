# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

"""
Replace the _call method to add more error handling
"""

import xmlrpclib
from openerp.addons.connector.exception import RetryableJobError
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    MagentoCRUDAdapter,
)


_call_orig = MagentoCRUDAdapter._call


def _call(self, method, arguments):
    try:
        result = _call_orig(self, method, arguments)
    except xmlrpclib.ProtocolError as err:
        # This error often appears with the Debonix' Magento (maybe
        # during upgrades of their system). If it happens on other
        # implementations, it should be moved in the generic magento
        # connector.
        if err.errcode == 302:
            raise RetryableJobError(
                'A protocol error caused the failure of the job:\n'
                'URL: %s\n'
                'HTTP/HTTPS headers: %s\n'
                'Error code: %d\n'
                'Error message: %s\n' %
                (err.url, err.headers, err.errcode, err.errmsg))

        else:
            raise
    except xmlrpclib.Fault as err:
        lock_msgs = ('SQLSTATE[40001]: Serialization failure: 1213 '
                     'Deadlock found when trying to get lock; try '
                     'restarting transaction',
                     'SQLSTATE[HY000]: General error: 1205 Lock wait '
                     'timeout exceeded; try restarting transaction',
                     )
        session_expired_msg = 'Session expired. Try to relogin.'
        # <Fault 404: 'Unknown error'>
        # retry because it seems to work when retried
        if err.faultCode == 404:
            raise RetryableJobError(
                "The job received <Fault 404: 'Unknown error'> "
                "from Magento.")
        elif err.faultCode == 1 and err.faultString in lock_msgs:
            # 1 means internal error
            raise RetryableJobError('Magento returned: "%s", possibly due '
                                    'to a reindexation in progress. '
                                    'This job will be retried later.' %
                                    err.faultString)
        elif err.faultCode == 5 and err.faultString == session_expired_msg:
            raise RetryableJobError('Magento returned: "%s".\n'
                                    'This job will be retried later.' %
                                    err.faultString)
        else:
            raise
    else:
        return result

MagentoCRUDAdapter._call = _call
