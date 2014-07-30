###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@helom_init @helom_stock

Feature: Setup Helom SARL company
   As an administrator, I do the following installation steps
   in order to setup the new Helom company stock setup

   @helom_add_base_stock
   Scenario: configure stock
   Given I need a "stock.location" with oid: helom.physical_location
     And having:
       | name                  | value                      |
       | name                  | Physical Locations         |
       | usage                 | view                       |
       | chained_location_type | none                       |
       | chained_auto_packing  | manual                     |
       | company_id            | by oid: helom.base_company |


     Given I need a "stock.location" with oid: helom.base_location
     And having:
       | name                  | value                           |
       | name                  | Helom                           |
       | usage                 | view                            |
       | location_id           | by oid: helom.physical_location |
       | chained_location_type | none                            |
       | chained_auto_packing  | manual                          |
       | company_id            | by oid: helom.base_company      |


     Given I need a "stock.location" with oid: helom.stock
     And having:
       | name                  | value                       |
       | name                  | Stock                       |
       | usage                 | internal                    |
       | location_id           | by oid: helom.base_location |
       | chained_location_type | none                        |
       | chained_auto_packing  | manual                      |
       | company_id            | by oid: helom.base_company  |

   Given I need a "stock.location" with oid: helom.virtual_location
     And having:
       | name                  | value                      |
       | name                  | Virtual Locations          |
       | usage                 | view                       |
       | chained_location_type | none                       |
       | chained_auto_packing  | manual                     |
       | company_id            | by oid: helom.base_company |

  Given I need a "stock.location" with oid: helom.loss
     And having:
       | name                  | value                          |
       | name                  | Inventory loss                 |
       | usage                 | view                           |
       | chained_location_type | none                           |
       | chained_auto_packing  | manual                         |
       | company_id            | by oid: helom.base_company     |
       | location_id           | by oid: helom.virtual_location |

  Given I need a "stock.location" with oid: helom.procurement
     And having:
       | name                  | value                          |
       | name                  | Procurement                    |
       | usage                 | procurement                    |
       | location_id           | by oid: helom.virtual_location |
       | chained_location_type | none                           |
       | chained_auto_packing  | manual                         |
       | company_id            | by oid: helom.base_company     |

  Given I need a "stock.location" with oid: helom.produciton
     And having:
       | name                  | value                          |
       | name                  | Production                     |
       | usage                 | production                     |
       | location_id           | by oid: helom.virtual_location |
       | chained_location_type | none                           |
       | chained_auto_packing  | manual                         |
       | company_id            | by oid: helom.base_company     |


   Given I need a "stock.location" with oid: helom.partner_location
     And having:
       | name                  | value                      |
       | name                  | Partner Locations          |
       | usage                 | view                       |
       | chained_location_type | none                       |
       | chained_auto_packing  | manual                     |
       | company_id            | by oid: helom.base_company |

  Given I need a "stock.location" with oid: helom.customer
     And having:
       | name                  | value                          |
       | name                  | Customers                      |
       | usage                 | customer                       |
       | chained_location_type | none                           |
       | chained_auto_packing  | manual                         |
       | company_id            | by oid: helom.base_company     |
       | location_id           | by oid: helom.partner_location |


  Given I need a "stock.location" with oid: helom.supplier
     And having:
       | name                  | value                          |
       | name                  | Suppliers                      |
       | usage                 | supplier                       |
       | location_id           | by oid: helom.partner_location |
       | chained_location_type | none                           |
       | chained_auto_packing  | manual                         |
       | company_id            | by oid: helom.base_company     |


  Given I need a "stock.location" with oid: helom.output
     And having:
       | name                  | value                       |
       | name                  | Output                      |
       | usage                 | internal                    |
       | location_id           | by oid: helom.base_location |
       | chained_location_type | customer                    |
       | chained_auto_packing  | manual                      |
       | company_id            | by oid: helom.base_company  |


  Given I need a "stock.warehouse" with oid: helom.warehouse
     And having:
       | name          | value                      |
       | name          | Helom wahrehouse           |
       | lot_input_id  | by oid: helom.stock        |
       | lot_output_id | by oid: helom.output       |
       | lot_stock_id  | by oid: helom.stock        |
       | company_id    | by oid: helom.base_company |

  Given I need a "sale.shop" with oid: helom.sale_shop
     And having:
       | name         | value                      |
       | name         | Helom shop                 |
       | company_id   | by oid: helom.base_company |
       | warehouse_id | by oid: helom.warehouse    |
       | pricelist_id | by oid: helom.eur_pl       |
