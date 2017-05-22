# -*- coding: utf-8 -*-
@upgrade_to_1.2.17 @debonix

Feature: upgrade to 1.2.17

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                 |
      | base_delivery_carrier_files          |
      | specific_function                    |
      | delivery_carrier_file_chronopost     |
      | delivery_carrier_label_colisprive    |
      | delivery_carrier_file_colissimo      |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.17"
