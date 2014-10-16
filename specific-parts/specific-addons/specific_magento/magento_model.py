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

import logging
from openerp.osv import orm
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    import_record,
)


_logger = logging.getLogger(__name__)


class magento_backend(orm.Model):
    _inherit = 'magento.backend'

    def select_versions(self, cr, uid, context=None):
        """ Available versions in the backend.

        Can be inherited to add custom versions.
        """
        versions = super(magento_backend, self).\
            select_versions(cr, uid, context=context)
        versions.append(('1.7-debonix', '1.7 - Debonix'))
        return versions

    def update_product_cost(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        mag_product_obj = self.pool.get('magento.product.product')
        product_ids = mag_product_obj.search(cr, uid,
                                             [('backend_id', 'in', ids)],
                                             context=context)
        _logger.info('Recompute Magento cost for %d products',
                     len(product_ids))
        mag_product_obj.recompute_magento_cost(cr, uid, product_ids,
                                               context=context)
        return True

    def _scheduler_update_product_cost(self, cr, uid, domain=None,
                                       context=None):
        self._magento_backend(cr, uid, self.update_product_cost,
                              domain=domain, context=context)

    def import_one_sale_order(self, cr, uid, ids, magento_id, context=None):
        """ Needed for the migration 5 to 7, we convert the 'need to update'
        sales orders to jobs so we need to create jobs directly """
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "1 ID expected"
            ids = ids[0]
        session = ConnectorSession(cr, uid, context=context)
        import_record.delay(session, 'magento.sale.order', ids, magento_id,
                            max_retries=0, priority=5)
