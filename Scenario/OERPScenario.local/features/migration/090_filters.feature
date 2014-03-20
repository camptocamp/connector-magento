@debonix @last  @migration

Feature: Configure things which must be done after all the other things... update or fix values

  @delivery @filters
  Scenario: I create default filters for stock.picking to replace v5 menu entries
    Given I need an "ir.filters" with oid: scenario.filter_picking_out_shop
    And having:
      | key        | value                                                                                                          |
      | name       | Colisage disponible Magasin                              |
      | model_id   | stock.picking.out                                        |
      | domain     | [['carrier_id', '=', False], ['state', '=', 'assigned']] |
      | context    | {'contact_display': 'partner'}                           |
      | user_id    | False                                                    |
      | is_default | False                                                    |
    Given I need an "ir.filters" with oid: scenario.filter_picking_out_exp
    And having:
      | key        | value                                                     |
      | name       | Colisage disponible Expédition                            |
      | model_id   | stock.picking.out                                         |
      | domain     | [['carrier_id', '!=', False], ['state', '=', 'assigned']] |
      | context    | {'contact_display': 'partner'}                            |
      | user_id    | False                                                     |
      | is_default | False                                                     |
