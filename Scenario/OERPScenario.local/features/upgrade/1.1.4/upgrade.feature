# -*- coding: utf-8 -*-
@upgrade_from_1.1.3 @debonix

Feature: upgrade to 1.1.4


  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | specific_fct                     |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- Recompute field min_qty
    UPDATE product_supplierinfo
    SET min_qty = 1.0
    WHERE id NOT IN (
        SELECT DISTINCT suppinfo_id
        FROM pricelist_partnerinfo
    );
    UPDATE product_supplierinfo
    SET min_qty = (
        SELECT MIN(min_quantity)
        FROM pricelist_partnerinfo
        WHERE pricelist_partnerinfo.suppinfo_id = product_supplierinfo.id
    );
    """

    Given I set the version of the instance to "1.1.4"
