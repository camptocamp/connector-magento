@debonix  @migration  @server_env

Feature: install the modules related to server environment

  Scenario: install main addons
    Given I install the required modules with dependencies:
      | name                         |
      | server_environment           |
      | server_environment_files     |
      | mail_environment             |
    Then my modules should have been installed and models reloaded

  @mail_setup_incoming
  Scenario: CREATE THE INCOMING MAIL SERVER
    Given I need a "fetchmail.server" with oid: scenario.openerp_incomming_claim
    And having:
    | name | value        |
    | name | imap_debonix |
    And I test and confirm the incomming mail server

  @mail_setup_outgoing
  Scenario: CREATE THE OUTGOING MAIL SERVER
    Given I need a "ir.mail_server" with oid: scenario.openerp_smtp_server
    And having:
    | name     | value        |
    | name     | smtp_debonix |
    | sequence | 1            |
