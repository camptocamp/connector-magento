# -*- coding: utf-8 -*-
@upgrade_to_1.2.9 @debonix

Feature: upgrade to 1.2.9

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                |
      | account_financial_report_webkit_csv |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.9"
