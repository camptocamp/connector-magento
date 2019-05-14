# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo.addons.connector_magento.models.partner.importer import (
    AddressImportMapper,
)


class DebonixAddressImportMapper(Component):
    _inherit = 'magento.address.import.mapper'
    _apply_on = 'magento.address'

    @property
    def direct(self):
        fields = super().direct
        if ('company', 'company') in fields:
            fields.remove(('company', 'company'))
        # TODO: 'mag_chronorelais_code' field is implemented
        # by 'delivery_carrier_file_chronopost'
        fields += [('w_relay_point_code', 'mag_chronorelais_code')]
        return fields

    @mapping
    def company(self, record):
        if record.get('w_relay_point_code'):
            return {'mag_chronorelais_company': record.get('company')}
        return {'company': record.get('company')}
