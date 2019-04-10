# -*- coding: utf-8 -*-
# © 2015 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields
from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  )
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    MagentoImportSynchronizer,
    )
from openerp.addons.magentoerpconnect.unit.backend_adapter import (
    MagentoCRUDAdapter,
    )
from .backend import magento_debonix


class magento_product_universe(orm.Model):
    _name = 'magento.product.universe'
    _inherit = 'magento.binding'
    _description = 'Magento Product Universe'

    _columns = {
        'name': fields.char(string='Name', required=True),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A product universe with same ID on Magento already exists.'),
    ]


@magento_debonix
class ProductUniverseImport(MagentoImportSynchronizer):
    """ Universe is an attribute in Magento """
    _model_name = ['magento.product.universe']

    MAGENTO_ATTRIBUTE_ID = 959

    def _get_magento_data(self):
        """ Return the raw Magento data for ``self.magento_id`` """
        backend_adapter = self.get_connector_unit_for_model(
            MagentoCRUDAdapter, 'magento.product.attribute')
        options = backend_adapter.options(self.MAGENTO_ATTRIBUTE_ID)
        for option in options:
            if option['value'] == str(self.magento_id):
                return option
        raise MappingError('On Magento, the product is configured with a '
                           'universe having an option with '
                           'the ID %s, but this option does not exist '
                           'on Magento' % self.magento_id)


@magento_debonix
class DebonixProductUniverseImportMapper(ImportMapper):
    _model_name = 'magento.product.universe'

    direct = [('label', 'name'),
              ]

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
