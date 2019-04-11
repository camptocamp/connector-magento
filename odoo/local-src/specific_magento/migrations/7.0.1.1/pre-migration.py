# -*- coding: utf-8 -*-
# © 2015 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    """ Move universes in another column to move them in post-migration.py """
    if not version:
        return
    logger.info("(pre-migration) specific_magento from version %s", version)
    logger.info("(pre-migration) renaming column magento_universe")
    cr.execute("ALTER TABLE magento_product_product "
               "RENAME COLUMN magento_universe "
               "TO magento_universe_migr")
