# -*- coding: utf-8 -*-
@upgrade_from_1.1.4 @debonix

Feature: upgrade to 1.1.5


  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- Put wrongly-excepted procurements as running
    UPDATE procurement_order
    SET state = 'running'
    WHERE id in (
        SELECT procurement_order.id
        FROM procurement_order
        LEFT JOIN wkf_instance ON procurement_order.id = wkf_instance.res_id
        LEFT JOIN wkf_workitem ON wkf_instance.id = wkf_workitem.inst_id
        WHERE wkf_instance.res_type = 'procurement.order'
        AND wkf_workitem.state = 'running'
        AND procurement_order.state = 'exception'
    );
    """

    Given I set the version of the instance to "1.1.5"
