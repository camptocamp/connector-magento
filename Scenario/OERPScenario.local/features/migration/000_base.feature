@debonix  @migration  @base

Feature: Migrate the database after the OpenERP migration

  Scenario: when we receive the database from the migration service, addons are 'to upgrade', set them to uninstalled.
    Given I execute the SQL commands
    """
    UPDATE ir_module_module set state = 'uninstalled' where state = 'to install';
    """

  @clean
  Scenario: clean the stuff of old modules
    Given I delete all the ir.ui.view records created by uninstalled modules
    And I delete all the ir.ui.menu records created by uninstalled modules
    And I delete all the ir.act_window records created by uninstalled modules
    And I delete all the ir.actions.act_window.view records created by uninstalled modules
    And I delete all the ir.act.report.xml records created by uninstalled modules
    And I delete all the ir.actions.todo records created by uninstalled modules
    And I delete all the ir.cron records created by uninstalled modules
    And I delete all the ir.module.repository records created by uninstalled modules
    And I delete all the ir.report.custom records created by uninstalled modules
    And I delete all the ir.report.custom.fields records created by uninstalled modules
    And I delete all the ir.ui.view_sc records created by uninstalled modules
    And I delete all the ir.values records created by uninstalled modules
    And I delete all the ir.rule records created by uninstalled modules
    And I delete all the ir.rule.group records created by uninstalled modules

  Scenario: install main addons
    Given I install the required modules with dependencies:
      | name               |
      | base               |
    Then my modules should have been installed and models reloaded
