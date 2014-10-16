@debonix  @migration  @picking_priority

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | stock_picking_priority             |
      | picking_priority_on_payment_method |
    Then my modules should have been installed and models reloaded

  Scenario: the priorities codes have been shifted to the left and the field has been renamed on sale_order
    Given I migrate the picking priorities modules
