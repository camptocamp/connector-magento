# -*- coding: utf-8 -*-
@upgrade_from_1.1.1 @debonix

Feature: upgrade to 1.1.2


  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                |
      | stock_picking_compute_delivery_date |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    DELETE FROM mail_message
    WHERE id NOT IN (
        SELECT max(id)
        FROM mail_message
        WHERE body ilike '%Scheduled date update%'
        GROUP BY res_id
    ) AND body ilike '%Scheduled date update%';
    """

    Given I set the version of the instance to "1.1.2"
