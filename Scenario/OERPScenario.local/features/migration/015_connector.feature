@debonix  @migration  @connector

Feature: install and configure the modules related to the magento connector

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                         |
      | magentoerpconnect            |
      | server_env_magentoerpconnect |
    Then my modules should have been installed and models reloaded

  @backend
  Scenario: Configure the magento backend
    Given I need a "magento.backend" with oid: scenario.magento_backend_debonix
    And having:
         | key                 | value                                                                            |
         | name                | debonix                                                                          |
         | version             | 1.7                                                                              |
         | warehouse_id        | by oid: stock.warehouse0                                                         |
         | default_lang_id     | by code: fr_FR                                                                   |
    # And I press the button "synchronize_metadata"
