# -*- coding: utf-8 -*-
@upgrade_from_1.0.9 @debonix

Feature: upgrade to 1.0.10


  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                     |
      | specific_fct             |
      | server_environment_files |
    Then my modules should have been installed and models reloaded

