# -*- coding: utf-8 -*-
@upgrade_from_1.1.7 @debonix

Feature: upgrade to 1.1.8

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | sale_dropshipping                |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- Set POs with destination address as dropshipping
    UPDATE purchase_order
    SET sale_flow = 'direct_delivery',
        invoice_method = 'order',
        sale_id = sale_order.id
    FROM sale_order
    WHERE dest_address_id IS NOT NULL
    AND sale_flow = 'normal'
    AND purchase_order.origin = sale_order.name;
    """

    Given I set the version of the instance to "1.1.8"
