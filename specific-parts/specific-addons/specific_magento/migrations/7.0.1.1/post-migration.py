# -*- coding: utf-8 -*-
# © 2015 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    logger.info("(post-migration) specific_magento from version %s", version)
    # previously hardcoded, we create records for them and remap the products
    selection = [
        ('909', 'EPI'),
        ('911', 'Jardin'),
        ('913', 'Quincaillerie'),
        ('923', 'Sanitaire'),
        ('931', 'Outillage'),
        ('935', 'Outillage à main'),
        ('953', 'Servante et rangement d''outillage'),
        ('965', 'Soudage'),
        ('967', 'Electricité'),
        ('991', 'Levage manutention'),
        ('993', 'Domotique'),
    ]
    cr.execute("SELECT id FROM magento_backend LIMIT 1")
    backend_id = cr.fetchone()[0]
    for key, name in selection:
        logger.info("(post-migration) moving %s universe to a record", name)
        cr.execute("""
            INSERT INTO magento_product_universe
            (backend_id, magento_id, name)
            VALUES
            (%s, %s, %s)
            RETURNING id
        """, (backend_id, key, name))
        record_id = cr.fetchone()[0]
        cr.execute("""
            UPDATE magento_product_product
            SET magento_universe_id = %s
            WHERE magento_universe_migr = %s
        """, (record_id, key))
    cr.execute("""
        ALTER TABLE magento_product_product
        DROP COLUMN magento_universe_migr
    """)
