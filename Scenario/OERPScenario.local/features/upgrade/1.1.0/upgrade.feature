# -*- coding: utf-8 -*-
@upgrade_1.1.0 @debonix

Feature: upgrade to 1.1.0


  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                |
      | purchase_group_hooks                |
      | sale_dropshipping                   |
      | sale_bom_split_dropshipping         |
      | magentoerpconnect                   |
      | account_export_csv                  |
      | account_easy_reconcile              |
      | account_advanced_reconcile          |
      | account_statement_base_completion   |
      | account_statement_base_import       |
      | account_statement_ext               |
      | base_transaction_id                 |
      | sale_exceptions                     |
      | last_sale_price                     |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.1.0"
