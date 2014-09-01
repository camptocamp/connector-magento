###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@helom_init

Feature: Setup Helom SARL company
   As an administrator, I do the following installation steps
   in order to setup the new Helom company

  @helom_pre_init
  Scenario: Preparation SQL
    Given  I execute the SQL commands
    """
    DELETE FROM ir_module_module WHERE name = 'l10n_ch';
    DELETE FROM ir_module_module WHERE name like 'l10n_ch%';
    UPDATE product_pricelist set company_id = 1 where company_id is NULL;
    UPDATE product_pricelist_version SET company_id = 1 WHERE company_id is NULL;
    UPDATE product_pricelist_item SET company_id = 1 WHERE company_id is NULL;
    UPDATE res_partner SET company_id = 1 WHERE company_id IS NULL;
    UPDATE ir_property set company_id = 1 WHERE company_id IS NULL;
    UPDATE product_template set company_id = 1 WHERE company_id is null;
    UPDATE  account_statement_profile SET company_id = 1 WHERE company_id IS NULL;

    """

  @helom_addons
  Scenario: INSTALL MODULES
    Given I update the module list
    Given I install the required modules with dependencies:
     | name            |
     | l10n_ch         |
     | sale_exceptions |
    Then my modules should have been installed and models reloaded

  Scenario: Post module upgrade SQL
    Given  I execute the SQL commands
    """
    UPDATE sale_exception set company_id = 1;
    """


  # Scenario: LANGUAGE INSTALL
  #   Given I install the following languages:
  #     | lang  |
  #     | de_DE |
  #     | it_IT |
  #   Then the language should be available


  # Scenario: LANGUAGE SETTINGS
  #   Given I need a "res.lang" with code: it_It
  #   And having:
  #    | name              | value     |
  #    | date_format       | %d/%m/%Y  |
  #    | grouping          | [3,0]     |
  #    | thousands_sep     | '         |
  #    Given I need a "res.lang" with code: de_DE
  #    And having:
  #    | name              | value     |
  #    | date_format       | %d/%m/%Y  |
  #    | grouping          | [3,0]     |
  #    | thousands_sep     | '         |


  @helom_company
  Scenario: Create a new company
    Given I need a "res.company" with oid helom.base_company
    And having:
      | name                 | value        |
      | name                 | Helom SARL   |
      | tracking_csv_path_in | /tmp         |
      | currency_id          | by name: EUR |
      # dummy value to fix in next scenario after locations creations
      | stockit_in_picking_location_id      | by name: Rebut |
      | stockit_in_picking_location_dest_id | by name: Rebut |
      | stockit_inventory_location_id       | by name: Rebut |

    Given I need a "res.partner" with oid: helom.base_partner
    And having:
     | name       | value                  |
     | street     | Rue Adrien-Lachenal 20 |
     | city       | Genève                 |
     | name       | Helom SARL             |
     | lang       | fr_FR                  |
     | website    |                        |
     | customer   | 1                      |
     | supplier   | 1                      |
     | zip        | 1207                   |
     | country_id | by code: CH            |


   Given I need a "res.company" with oid: helom.base_company
   And having:
     | name       | value                      |
     | partner_id | by oid: helom.base_partner |


  @helom_rml_header
  Scenario: Set RML header
  Given I set RML header to company with oid "helom.base_company" using "Helom/header_rml.txt" file

  @helom_fiscal_year
  Scenario: fiscal year
    Given I need a "account.fiscalyear" with oid: helom.fy2014
    And having:
       | name       | value                      |
       | name       | CH2014                     |
       | code       | CH2014                     |
       | date_start | 2014-01-01                 |
       | date_stop  | 2014-12-31                 |
       | company_id | by oid: helom.base_company |

    And I create monthly periods on the fiscal year with reference "helom.fy2014"
    Then I find a "account.fiscalyear" with oid: helom.fy2014

  @helom_admin_user
  Scenario: Helom admin user
  Given I need a "res.users" with oid: helom.admin_user
     And having:
     | name        | value                          |
     | name        | Helom admin                    |
     | login       | admin_ch                       |
     | password    | admin_ch                       |
     | lang        | fr_FR                          |
     | company_id  | by oid: helom.base_company     |
     | company_ids | all by oid: helom.base_company |

  Given we select users below:
        | login    |
        | admin_ch |
  Then we assign all groups to the users

  @helom_change_base_partner_company
  Scenario: Set company on base partner

    Given I need a "res.partner" with oid: helom.base_partner
    And having:
     | name       | value                      |
     | company_id | by oid: helom.base_company |


  @helom_admin_user
  Scenario: Debonix admin user
  Given I need a "res.users" with oid: debonix.admin_user
     And having:
     | name        | value                         |
     | name        | Debonix admin                 |
     | login       | admin_fr                      |
     | password    | admin_fr                      |
     | lang        | fr_FR                         |
     | company_id  | by oid: base.main_company     |
     | company_ids | all by oid: base.main_company |

  Given we select users below:
        | login    |
        | admin_fr   |
  Then we assign all groups to the users


  Scenario Cleanup group generated by share function
    Given  I execute the SQL commands
    """
        SELECT * FROM res_groups_users_rel WHERE gid = 97 AND uid != 93;
    """
  @helom_account_chart
  Scenario: Account chart
    Given I have the module account installed
    And no account set for company "Helom SARL"
    And I want to generate account chart from chart template named "Plan comptable STERCHI" with "0" digits for company "Helom SARL"
    When I generate the chart
    Then accounts should be available for company "Helom SARL"

Scenario: fix currency to EUR after Account chart installation
    Given I need a "res.company" with oid helom.base_company
    And having:
      | name        | value        |
      | currency_id | by name: EUR |
