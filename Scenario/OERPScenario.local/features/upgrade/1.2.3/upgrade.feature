# -*- coding: utf-8 -*-
@upgrade_from_1.2.2 @debonix

Feature: upgrade to 1.2.3

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                 |
      | debonix_purchase_edi |
      | specific_fct         |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.3"