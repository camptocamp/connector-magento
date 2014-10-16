# -*- coding: utf-8 -*-
@upgrade_from_1.0.4 @debonix

Feature: upgrade to 1.0.5

  # upgrade of specific-addons for delivery_carrier_file monkey patching

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                      |
      | base                      |
    Then my modules should have been installed and models reloaded


    Given I set the version of the instance to "1.0.5"
