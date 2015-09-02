# -*- coding: utf-8 -*-
@upgrade_from_1.1 @debonix

Feature: upgrade to 1.2.0

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | connector                        |
      | magentoerpconnect                |
      | server_env_magentoerpconnect     |
      | specific_magento                 |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- Clean unsynched prices when a synced price exists
    DELETE FROM pricelist_partnerinfo
    WHERE (from_magento = False OR from_magento IS NULL)
    AND suppinfo_id IN (
        SELECT suppinfo_id
        FROM pricelist_partnerinfo
        WHERE from_magento = True
    );

    -- Called twice for one case with triplet
    DELETE FROM pricelist_partnerinfo
    WHERE id IN (
        SELECT min_id
        FROM (
            SELECT count(*) as cnt,
            min(id) as min_id
            FROM pricelist_partnerinfo
            GROUP BY suppinfo_id, min_quantity
        ) AS foo
        WHERE cnt > 1
    );

    DELETE FROM pricelist_partnerinfo
    WHERE id IN (
        SELECT min_id
        FROM (
            SELECT count(*) as cnt,
            min(id) as min_id
            FROM pricelist_partnerinfo
            GROUP BY suppinfo_id, min_quantity
        ) AS foo
        WHERE cnt > 1
    );

    -- Fix products with wrong magento ID
    UPDATE magento_product_product
    SET magento_id = 39695
    WHERE id = 28410;

    UPDATE magento_product_product
    SET magento_id = 19357
    WHERE id = 10590;
    """

    Given I set the version of the instance to "1.2.0"
