# -*- coding: utf-8 -*-
@upgrade_to_1.2.16 @debonix

Feature: upgrade to 1.2.15

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                 |
      | specific_fct                         |
      | base_delivery_carrier_label          |
      | base_delivery_carrier_files_document |
      | delivery_carrier_label_colisprive    |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.16"
