# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component

from odoo.addons.connector_magento.components.backend_adapter import (
    MAGENTO_DATETIME_FORMAT,
)


class DebonixProductProductAdapter(Component):
    _inherit = 'magento.product.product.adapter'

    def search(self, filters=None, from_date=None, to_date=None):
        """ Search records according to some criteria
        and returns a list of ids

        :rtype: list
        """
        if filters is None:
            filters = {}
        dt_fmt = MAGENTO_DATETIME_FORMAT
        if from_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date.strftime(dt_fmt)
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date.strftime(dt_fmt)
        magento_ids = self._call('%s.search' % self._magento_model,
                                 [filters] if filters else [{}])
        return (int(magento_id) for magento_id in magento_ids)
