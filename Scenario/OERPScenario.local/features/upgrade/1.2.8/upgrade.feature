# -*- coding: utf-8 -*-
@upgrade_to_1.2.8 @debonix

Feature: upgrade to 1.2.8

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | delivery_carrier_file_chronopost |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.8"
