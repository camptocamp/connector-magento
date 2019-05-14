# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import os

from odoo.addons.connector_magento.tests.common import (
    MagentoSyncTestCase, recorder,
)


class TestImportPartner(MagentoSyncTestCase):

    def setUp(self):
        super().setUp()
        category_model = self.env['res.partner.category']
        existing_category = category_model.create({'name': 'General'})
        self.create_binding_no_export(
            'magento.res.partner.category',
            existing_category,
            1
        )
        self.model = self.env['magento.res.partner']
        self.address_model = self.env['magento.address']

    @recorder.use_cassette
    def test_import_partner_individual_1_address(self):
        """ Import an individual (b2c) with 1 billing address

        A magento customer is considered an individual if its billing
        address has an empty 'company' field
        """
        self.env['magento.res.partner'].import_record(self.backend, '136')
        partner = self.model.search([('external_id', '=', '136'),
                                     ('backend_id', '=', self.backend.id)])
        address_bind = partner.magento_address_bind_ids[0]
        # 'company' not mapped anymore
        self.assertEqual(address_bind.company, False)
