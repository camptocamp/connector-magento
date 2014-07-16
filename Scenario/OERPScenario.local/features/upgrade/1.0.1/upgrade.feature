# -*- coding: utf-8 -*-
@upgrade_from_1.0.0 @debonix

Feature: upgrade to 1.0.1

  Scenario: upgrade application version
    #Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name            |
      | stockit_synchro |
    Given I uninstall the following modules:
      | name                               |
      | picking_priority_on_payment_method |
      | stock_picking_priority             |
    Then my modules should have been installed and models reloaded

  Scenario: upgrade application version
    Given I set the version of the instance to "1.0.1"
