# -*- coding: utf-8 -*-
@upgrade_from_1.0.1 @debonix

Feature: upgrade to 1.0.2

  Scenario: upgrade application version
    Given I execute the SQL commands
    """
    DELETE FROM ir_sequence_type WHERE code = 'stock.picking';
    UPDATE ir_sequence_type SET code = 'stock.picking' where name = 'Picking INT';
    UPDATE ir_sequence SET code = 'stock.picking' where name = 'Picking INT';
    UPDATE ir_sequence SET active = False where name = 'Packing';
    """

    Given I set the version of the instance to "1.0.2"
