@debonix  @migration  @accounting

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | account_tid_reconcile              |
      | currency_rate_update               |
    Then my modules should have been installed and models reloaded

  @journal_type
  Scenario: The journal have new types
    Given I find an "account.journal" with code: AVTE
    And having:
      | name | value       |
      | type | sale_refund |
    Given I find an "account.journal" with code: AACH
    And having:
      | name | value           |
      | type | purchase_refund |
