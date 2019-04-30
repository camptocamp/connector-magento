# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import xmlrpc.client

from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import RetryableJobError


class DebonixMagentoCRUDAdapter(AbstractComponent):
    _inherit = 'magento.crud.adapter'

    def _call(self, method, arguments):
        """Overload the method to add more error handling."""
        try:
            result = super()._call(method, arguments)
        except xmlrpc.client.ProtocolError as err:
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
        except xmlrpc.client.Fault as err:
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
