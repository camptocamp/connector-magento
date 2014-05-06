@debonix  @migration  @various

Feature: install various modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                           |
      | intrastat_base                 |
      | l10n_fr_intrastat_product      |
      | base_partner_merge             |
    Then my modules should have been installed and models reloaded
