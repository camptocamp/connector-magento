@debonix  @migration  @server_env

Feature: install the modules related to server environment

  Scenario: install main addons
    Given I install the required modules with dependencies:
      | name                         |
      | server_environment           |
      | server_environment_files     |
    Then my modules should have been installed and models reloaded
