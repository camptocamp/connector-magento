@debonix  @migration  @accounting

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | account_tid_reconcile              |
      | currency_rate_update               |
    Then my modules should have been installed and models reloaded
