@debonix  @migration  @connector

Feature: install the modules related to server environment

  Scenario: install main addons
    Given I install the required modules with dependencies:
      | name                         |
      | magentoerpconnect            |
      | server_env_magentoerpconnect |
    Then my modules should have been installed and models reloaded
