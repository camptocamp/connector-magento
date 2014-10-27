# -*- coding: utf-8 -*-
@upgrade_from_1.0.4 @debonix

Feature: upgrade to 1.0.5
  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  # !!!!!!!!!!!!!!!!!!! This tag will also install HELOM company !!!!!!!!!
  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

  Scenario: upgrade application version
#    Given I update the module list
#    Given I install the required modules with dependencies:
#    | name                                |
#    | stock_picking_compute_delivery_date |
#    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.0.5"
