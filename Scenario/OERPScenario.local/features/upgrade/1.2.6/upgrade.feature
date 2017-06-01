# -*- coding: utf-8 -*-
@upgrade_to_1.2.6 @debonix

Feature: upgrade to 1.2.6

  Scenario: update all product's cost method
    Given I execute the SQL commands
    """
    UPDATE product_template
    SET cost_method = 'average'
    WHERE cost_method = 'standard';
    """

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                 |
      | last_purchase_price  |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.6"