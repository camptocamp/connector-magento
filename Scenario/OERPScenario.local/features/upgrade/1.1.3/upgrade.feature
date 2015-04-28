# -*- coding: utf-8 -*-
@upgrade_from_1.1.3 @debonix

Feature: upgrade to 1.1.3


  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I execute the SQL commands
    """
    -- Rename base_login_date_improvement as base_concurrency
    UPDATE ir_model_data
    SET module='base_concurrency'
    WHERE module='base_login_date_improvement'
    AND model like 'ir.model%';
    UPDATE ir_module_module set state='to remove' where name='base_login_date_improvement';
    """
    Given I uninstall the following modules:
      | name                             |
      | base_login_date_improvement      |
    Given I install the required modules with dependencies:
      | name                             |
      | base_concurrency                 |
      | specific_fct                     |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.1.3"
