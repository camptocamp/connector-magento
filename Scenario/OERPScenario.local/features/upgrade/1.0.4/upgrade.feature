# -*- coding: utf-8 -*-
@upgrade_from_1.0.3 @debonix

Feature: upgrade to 1.0.4

  Scenario: upgrade application version
    Given I execute the SQL commands
    """
    UPDATE res_partner SET customer = 't' WHERE id IN 
    (SELECT c.id FROM res_partner c LEFT JOIN res_partner p ON c.parent_id = p.id 
    WHERE c.customer is null AND p.parent_id is null AND p.customer = 't');
    UPDATE res_partner SET supplier = 't' WHERE id IN
    (SELECT c.id FROM res_partner c LEFT JOIN res_partner p ON c.parent_id = p.id
    WHERE c.supplier is null AND p.parent_id is null AND p.supplier = 't');
    """

    Given I set the version of the instance to "1.0.4"
