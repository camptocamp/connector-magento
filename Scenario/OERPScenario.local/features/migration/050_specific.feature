@debonix  @migration  @specific

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | specific_fct                       |
      | specific_magento                   |
    Then my modules should have been installed and models reloaded
