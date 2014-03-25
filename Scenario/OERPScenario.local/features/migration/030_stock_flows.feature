@debonix  @migration  @stock_flows

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | product_multi_ean                  |
      | stock_split_picking                |
      | stockit_synchro                    |
      | stock_values_csv                   |
    Then my modules should have been installed and models reloaded
