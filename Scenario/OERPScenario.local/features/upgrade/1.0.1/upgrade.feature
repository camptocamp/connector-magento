# -*- coding: utf-8 -*-
@upgrade_from_1.0.0 @debonix

Feature: upgrade to 1.0.1

  Scenario: upgrade application version
    #Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                      |
      | stockit_synchro           |
      | stock_picking_mass_assign |
    Given I uninstall the following modules:
      | name                               |
      | picking_priority_on_payment_method |
      | stock_picking_priority             |
    Then my modules should have been installed and models reloaded

    Given I find a possibly inactive "ir.cron" with oid: stock_picking_mass_assign.ir_cron_check_assign_all
    And having:
      | name   | value |
      | active | true  |

    Given I execute the SQL commands
    """
    DELETE FROM ir_cron WHERE name = 'Try to assign all confirmed outgoing packings';
    """

    Given I set the version of the instance to "1.0.1"
