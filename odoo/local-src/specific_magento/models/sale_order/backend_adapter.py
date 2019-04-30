# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class DebonixSaleOrderAdapter(Component):
    """ Adapt the Adapter for Debonix

    Only import sales orders that are already paid in Magento,
    so we avoid to have pending jobs for unpaid orders that
    are retried many times.

    The downside is that jobs for the same orders will be created
    several times, but they will return eagerly so that's not
    so much of a problem.

    """
    _inherit = 'magento.sale.order.adapter'

    ignored_status = ('canceled',
                      'closed',
                      'complete',
                      'expired',
                      'fraud',
                      'pending',
                      'pending_payzen',
                      'pending_kwx',
                      'pending_payment',
                      'payment_refused',
                      'pending_vadsmulti',
                      'holded',
                      'pending_paypal',
                      'payment_review',
                      )

    def search(self, filters=None, from_date=None, to_date=None,
               magento_storeview_ids=None):
        """ Search records according to some criteria
        and returns a list of ids

        :rtype: list
        """
        if filters is None:
            filters = {}
        dt_fmt = '%Y/%m/%d %H:%M:%S'
        if from_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date.strftime(dt_fmt)
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date.strftime(dt_fmt)
        if magento_storeview_ids is not None:
            filters['store_id'] = {'in': magento_storeview_ids}

        filters['total_paid'] = {'gt': 0.}
        filters['status'] = {'nin': self.ignored_status}

        arguments = {'imported': False,
                     'filters': filters,
                     }
        return self._call('%s.search' % self._magento_model, [arguments])

    def set_expected_date(self, item_id, expected_date):
        """ Update the delivery date on Magento

        :param item_id: the ID of the sale line on Magento
        :param expected_date: the date
        """
        _logger.info('%s.update_shipping_delay(%s)',
                     self._magento_model,
                     [item_id, expected_date])
        return self._call('%s.update_shipping_delay'
                          % self._magento_model,
                          [item_id, expected_date])
