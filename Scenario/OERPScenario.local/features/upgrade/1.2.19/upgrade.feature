# -*- coding: utf-8 -*-
@upgrade_to_1.2.19 @debonix

Feature: upgrade to 1.2.19

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                 |
      | specific_fct                         |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.19"