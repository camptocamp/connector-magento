# -*- coding: utf-8 -*-
@upgrade_from_1.0.8 @debonix

Feature: upgrade to 1.0.9


  Scenario: upgrade application version
 #    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
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

  Scenario: Set Uk as origin country for ToolStream (France)
    Given I execute the SQL commands
    """
    -- I update Toolstream partner
    UPDATE res_partner set origin_country_id = 222 where id in (46,71628);
    -- I update supplier info linked with partner Toolstream
    UPDATE product_supplierinfo set origin_country_id = 222 where name in (46,71628);
    -- I update supplier Festool
    UPDATE res_partner set origin_country_id = 56 where id = 32;
    UPDATE product_supplierinfo set origin_country_id = 56 where name = 32;
    """

    Given I set the version of the instance to "1.0.9"
