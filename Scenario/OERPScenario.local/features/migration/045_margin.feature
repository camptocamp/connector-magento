@debonix  @migration  @margin

Feature: install and configure the equivalence of products

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name             |
      | sale_markup      |
      | sale_floor_price |
    Then my modules should have been installed and models reloaded
