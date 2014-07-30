###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################
@helom_init @helom_pricelist

Feature: Setup Helom pricelist
   As an administrator, I do the following installation steps
   in order to setup the new Helom company price list

   Scenario: Base price list
     Given I need a "product.pricelist" with oid: helom.eur_pl
     And having:
     | name        | value                      |
     | name        | HELOM EUR SALE             |
     | currency_id | by name: EUR               |
     | type        | sale                       |
     | company_id  | by oid: helom.base_company |

   Given I need a "product.pricelist" with oid: helom.eur_pl_pur
     And having:
     | name        | value                      |
     | name        | HELOM EUR PUCHASE          |
     | currency_id | by name: EUR               |
     | type        | purchase                   |
     | company_id  | by oid: helom.base_company |

  @helom_default_pricelist
  Scenario: Set global property property_product_pricelist 
    Given I set global property named "property_product_pricelist" for model "res.partner" and field "property_product_pricelist" for company with ref "helom.base_company"
    And the property is related to model "product.pricelist" using column "name" and value "HELOM EUR SALE"

  @helom_default_pricelist
  Scenario: Set global property property_product_pricelist 
    Given I set global property named "property_product_pricelist_purchase" for model "res.partner" and field "property_product_pricelist_purchase" for company with ref "helom.base_company"
    And the property is related to model "product.pricelist" using column "name" and value "HELOM EUR PUCHASE"
