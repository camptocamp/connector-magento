@debonix  @migration  @equivalence

Feature: install and configure the equivalence of products

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                         |
     | packing_product_change |
     | product_equivalence    |
    Then my modules should have been installed and models reloaded

  Scenario: Migrate data because the field c2c_debonix_equiv has been renamed to equivalent_id
    Given I execute the SQL commands
    """
    update product_product set equivalent_id = c2c_debonix_equiv where c2c_debonix_equiv is not null and equivalent_id is null;
    """
