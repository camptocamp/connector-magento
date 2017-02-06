# -*- coding: utf-8 -*-
@upgrade_to_1.2.14 @debonix

Feature: upgrade to 1.2.14

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                 |
      | debonix_purchase_edi |
      | specific_fct         |
      | specific_magento     |
    Then my modules should have been installed and models reloaded

  Scenario: change UoM on products + add keys on UoMs
    Given I execute the SQL commands
    """
        UPDATE product_uom
        SET magento_name = 'PCE', edi_code = 'P'
        WHERE id = 1;
        UPDATE product_uom
        SET magento_name = 'M', edi_code = 'M'
        WHERE id = 3;
    """

    Given I set the version of the instance to "1.2.14"
