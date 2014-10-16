@debonix  @migration  @stock_flows

Feature: install and migrate the picking priorities modules
  For each packing, I need to generate a file for the carrier (chronopost).
  For this purpose, I use the generic module base_delivery_carrier_files and a sub-module
  which defines the file.

  I also need to import tracking numbers on the packings.

  @slow
  Scenario: install addons
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | product_multi_ean                |
      | stock_split_picking              |
      | stockit_synchro                  |
      | stock_values_csv                 |
      | bom_stock                        |
      | base_delivery_carrier_files      |
      | delivery_carrier_file_chronopost |
      | import_tracking                  |
      | bom_split                        |
      | sale_bom_split                   |
      | purchase_bom_split               |
      | sale_jit_on_services             |
    Then my modules should have been installed and models reloaded

  Scenario: I need to create the carrier file configuration because it is now represented in carrier.file
    Given I need a "delivery.carrier.file" with name: Chronopost and oid: scenario.chronopost
    And having:
      | name        | value                                                               |
      | type        | chronopost                                                          |
      | auto_export | true                                                                |
      | write_mode  | disk                                                                |
      | export_path | /srv/openerp/instances/openerp_prod_debonix/shipping_smb/chronopost |

  Scenario: I need to create the carrier file configuration for chronorelais
    Given I need a "delivery.carrier.file" with name: Chronorelais and oid: scenario.chronorelais
    And having:
      | name        | value                                                                 |
      | type        | chronorelais                                                          |
      | auto_export | true                                                                  |
      | write_mode  | disk                                                                  |
      | export_path | /srv/openerp/instances/openerp_prod_debonix/shipping_smb/chronorelais |

  Scenario: I need to create the carrier file configuration for Calbersonp
    Given I need a "delivery.carrier.file" with name: Calbersonp and oid: scenario.calbersonp
    And having:
      | name        | value                                                                 |
      | type        | chronopost                                                            |
      | auto_export | true                                                                  |
      | write_mode  | disk                                                                  |
      | export_path | /srv/openerp/instances/openerp_prod_debonix/shipping_smb/calbersonp   |

  Scenario: I need to create the carrier file configuration for Owebiashipping2
    Given I need a "delivery.carrier.file" with name: Owebiashipping2 and oid: scenario.owebiashipping2
    And having:
      | name        | value                                                                    |
      | type        | chronopost                                                               |
      | auto_export | true                                                                     |
      | write_mode  | disk                                                                     |
      | export_path | /srv/openerp/instances/openerp_prod_debonix/shipping_smb/owebiashipping2 |

  Scenario: Previously, the chronopost subaccount was stored on the company, it has now moved on the
          # delivery.carrier.file configuration, as the field on company does not more exist for openerp
          # I run a SQL update to set the sub-account on the carrier file
    Given I execute the SQL commands
    """
        -- update all records as they are all based on chronopost
        update delivery_carrier_file
        set subaccount_number = (select chronopost_subaccount_number from res_company where id = 1);
    """

  @set_chronopost_carrier_file
  Scenario: Actually, a lot of delivery method exists for Chronopost
          # I need to configure them to use the chronopost carrier file
          # So I link the carrier file configuration with all the chronopost delivery methods
    Given I want to modify all the delivery methods linked with "CHRONOPOST" partner
    Then I set their values to:
      | key             | value                       |
      | carrier_file_id | by oid: scenario.chronopost |

  @set_chronopost_carrier_file
  Scenario Outline: assign the delivery methods to their carrier file (only the output directory changes)
    Given I find a "delivery.carrier" with name: <name>
    Then I set their values to:
      | key             | value                               |
      | carrier_file_id | by oid: <carrier_file_oid>          |

    Examples: on owebiashipping2 (chronopost is not an error)
      | name                                   | carrier_file_oid         |
      | owebiashipping2_chronopost_chronopost3 | scenario.owebiashipping2 |
      | chronopost_chronopost                  | scenario.owebiashipping2 |
      | owebiashipping2_chronopost_offert      | scenario.owebiashipping2 |
      | owebiashipping2_chronopost_corse       | scenario.owebiashipping2 |
      | owebiashipping2_chronopost             | scenario.owebiashipping2 |

    Examples: on chronorelais
      | name                      | carrier_file_oid      |
      | chronorelais_chronorelais | scenario.chronorelais |

    Examples: on calbersonp
      | name       | carrier_file_oid    |
      | calbersonp | scenario.calbersonp |


  Scenario: We have used a field packages_number on stock.picking, in 6.1 this fields exists in the delivery module
     # with name number_of_packages, so we migrate the data
    Given I execute the SQL commands
    """
       update stock_picking set number_of_packages = package_number where number_of_packages isnull;
       """

  @backend
  Scenario: set the bom_stock field on the magento backend
    Given I find a "magento.backend" with oid: scenario.magento_backend_debonix
    And having:
         | key                    | value              |
         | product_stock_field_id | by name: bom_stock |

  @recompute_magento_qty @slow
  Scenario: recompute the quantity on all products
    Given I find a "magento.backend" with oid: scenario.magento_backend_debonix
    And I recompute the magento stock quantities without export

  @fix_done_picking
  Scenario: Fix a bug of V5: all the moves of a done picking must be done
    Given I execute the SQL commands
    """
    UPDATE stock_move SET state = 'done' WHERE id IN (
      SELECT m.id FROM stock_move m INNER JOIN stock_picking s ON s.id = m.picking_id WHERE s.state = 'done' AND m.state != 'done'
    )
    """

  @location_name
  Scenario: Copy the translation of the stock locations to the name of the location because it can be confusive
    Given I execute the SQL commands
    """
      -- duplicate and wrong translation for 'Votre société' location
      UPDATE ir_translation SET value = 'Debonix' WHERE res_id = 9 and name = 'stock.location' and xml_id = 'stock_location_company';
      DELETE FROM ir_translation WHERE res_id = 9 and name = 'stock.location' and xml_id IS NULL;
      -- copy translations in source
      UPDATE stock_location AS s SET name = tr.value FROM ir_translation tr WHERE tr.res_id = s.id and tr.lang = 'fr_FR' and tr.name = 'stock.location,name';
      -- too long to use the ORM write
      UPDATE stock_location SET complete_name = 'Emplacements physiques / Debonix / Stock' WHERE id = 11;
    """
    And I recompute complete_name on stock.location
