# -*- coding: utf-8 -*-
@upgrade_from_1.1.10 @debonix

Feature: upgrade to 1.1.11

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.1.11"
