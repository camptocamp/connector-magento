# -*- coding: utf-8 -*-
@upgrade_from_1.1.5 @debonix

Feature: upgrade to 1.1.6


  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.1.6"
