@debonix  @migration  @stock_flows

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | stock_split_picking                |
      | stockit_synchro                    |
    Then my modules should have been installed and models reloaded
