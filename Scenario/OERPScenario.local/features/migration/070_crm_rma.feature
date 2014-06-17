@debonix  @migration  @rma

Feature: install various modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name        |
      | openerp_rma |
    Then my modules should have been installed and models reloaded
