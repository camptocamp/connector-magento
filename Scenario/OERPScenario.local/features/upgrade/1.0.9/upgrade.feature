# -*- coding: utf-8 -*-
@upgrade_from_1.0.8 @debonix

Feature: upgrade to 1.0.9


  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                |
      | specific_fct                        |
      | stock_picking_compute_delivery_date |
    Then my modules should have been installed and models reloaded

  Scenario: copy gross weight to net weight
    Given I execute the SQL commands
    """
    UPDATE product_template
    SET weight_net = weight
    WHERE (weight_net = 0.0 OR weight_net IS NULL)
    AND (weight IS NOT NULL AND weight > 0.0);
    """

  Scenario: remove unnecessary messages
    Given I execute the SQL commands
    """
    DELETE FROM mail_message
    WHERE model = 'product.product'
    AND body ILIKE '<p>Scheduled date update to %';
    """

    Given I set the version of the instance to "1.0.9"
