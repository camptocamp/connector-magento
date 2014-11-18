# -*- coding: utf-8 -*-
@upgrade_from_1.0.6 @debonix

Feature: upgrade to 1.0.7

  # upgrade of specific-addons for delivery_carrier_file monkey patching

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                |
      | account_easy_reconcile              |
      | base_partner_merge                  |
      | connector_ecommerce                 |
      | sale_floor_price                    |
      | sale_markup                         |
      | sale_line_watcher                   |
      | specific_sale_exceptions            |
      | stock_picking_compute_delivery_date |
      | specific_fct                        |
    Then my modules should have been installed and models reloaded


    Given I set the version of the instance to "1.0.7"
