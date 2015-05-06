# -*- coding: utf-8 -*-
@upgrade_from_1.1.3 @debonix

Feature: upgrade to 1.1.4


  Scenario: upgrade application version
    Given I update the module list
    Given I execute the SQL commands
    """
    -- Rename base_login_date_improvement as base_concurrency
    Given I install the required modules with dependencies:
      | name                             |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.1.4"
