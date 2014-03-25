@debonix  @migration  @stock_flows

Feature: install and migrate the picking priorities modules
  For each packing, I need to generate a file for the carrier (chronopost).
  For this purpose, I use the generic module base_delivery_carrier_files and a sub-module
  which defines the file.

  I also need to import tracking numbers on the packings.


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
    Then my modules should have been installed and models reloaded

  Scenario: I need to create the carrier file configuration because it is now represented in carrier.file
          # I have to create the configuration for chronopost and bind each delivery method to it
    Given I need a "delivery.carrier.file" with name: Chronopost and oid: scenario.chronopost
    And having:
      | name        | value      |
      | type        | chronopost |
      | auto_export | true       |
      | write_mode  | disk       |

  Scenario: Previously, the chronopost subaccount was stored on the company, it has now moved on the
          # delivery.carrier.file configuration, as the field on company does not more exist for openerp
          # I run a SQL update to set the sub-account on the carrier file
    Given I execute the SQL commands
    """
        update delivery_carrier_file
        set subaccount_number = (select chronopost_subaccount_number from res_company where id = 1)
        where id in (select res_id from ir_model_data where model = 'delivery.carrier.file' and module = 'scenario' and name = 'chronopost')
        """

  @set_chronopost_carrier_file
  Scenario: Actually, a lot of delivery method exists for Chronopost
          # I need to configure them to use the chronopost carrier file
          # So I link the carrier file configuration with all the chronopost delivery methods
    Given I want to modify all the delivery methods linked with "CHRONOPOST" partner
    Then I set their values to:
      | key             | value                       |
      | carrier_file_id | by oid: scenario.chronopost |

  Scenario: We have used a field packages_number on stock.picking, in 6.1 this fields exists in the delivery module
     # with name number_of_packages, so we migrate the data
    Given I execute the SQL commands
    """
       update stock_picking set number_of_packages = package_number where number_of_packages isnull;
       """

  Scenario: To import the tracking numbers, I have already created a directory in the document.feature
          # Now, I link my company setup to this directory
    Given I need a "res.company" with oid: base.main_company
    And having:
      | name                  | value                            |
      | tracking_directory_id | by oid: scenario.import_tracking |

  @backend
  Scenario: set the bom_stock field on the magento backend
    Given I find a "magento.backend" with oid: scenario.magento_backend_debonix
    And having:
         | key                    | value              |
         | product_stock_field_id | by name: bom_stock |
