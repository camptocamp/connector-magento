###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@helom_init @helom_custom_chart

Feature: As an administrator, I do the following installation steps
         in order to setup custom account chart

  @helom_custom_chart
  Scenario: custom chart
    Given  I execute the SQL commands
    """
    DELETE FROM account_account where company_id != 1;
    """
    Given "account.account" is imported from CSV "Helom/Helom_CoA.csv" using delimiter ","

  @helom_default_accounts
  Scenario: Set global property property_account_receivable
    Given I set global property named "property_account_receivable" for model "res.partner" and field "property_account_receivable" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "411000"

  @helom_default_accounts
  Scenario: Set global property property_account_payable
    Given I set global property named "property_account_payable" for model "res.partner" and field "property_account_payable" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "401000"

  @helom_default_accounts
  Scenario: Set global property property_account_expense_categ
    Given I set global property named "property_account_expense_categ" for model "product.category" and field "property_account_expense_categ" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "607100"

  @helom_default_accounts
  Scenario: Set global property property_account_income_categ
    Given I set global property named "property_account_income_categ" for model "product.category" and field "property_account_income_categ" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "707000"

  @helom_default_accounts
  Scenario: Set global property property_account_expense
    Given I set global property named "property_account_expense" for model "product.template" and field "property_account_expense" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "607100"

  @helom_default_accounts
  Scenario: Set global property property_account_income
    Given I set global property named "property_account_income" for model "product.template" and field "property_account_income" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "707000"

  @helom_default_accounts
 Scenario: Set global property property_stock_account_input
    Given I set global property named "property_stock_account_input" for model "product.template" and field "property_stock_account_input" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "603710"

  @helom_default_accounts
 Scenario: Set global property property_stock_account_output
    Given I set global property named "property_stock_account_output" for model "product.template" and field "property_stock_account_output" for company with ref "helom.base_company"
    And the property is related to model "account.account" using column "code" and value "603710"


  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 8.0%
    And having:
    | name                 | value                      |
    | account_collected_id | by name:  TVA collectée 8% |
    | account_paid_id      | by name:  TVA collectée 8% |


  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 8.0% achat
    And having:
    | name                 | value                                   |
    | account_collected_id | by name: TVA sur Biens et Services à 8% |
    | account_paid_id      | by name: TVA sur Biens et Services à 8% |

  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 100% imp.
    And having:
    | name                 | value                                   |
    | account_collected_id | by name: TVA sur Biens et Services à 8% |
    | account_paid_id      | by name: TVA sur Biens et Services à 8% |


  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 2.5% achat
    And having:
    | name                 | value                                   |
    | account_collected_id | by name: TVA sur Biens et Services à 8%   |
    | account_paid_id      | by name: TVA sur Biens et Services à 8%  |


  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 3.8% achat
    And having:
    | name                 | value                                     |
    | account_collected_id | by name: TVA sur Biens et Services à 3.8% |
    | account_paid_id      | by name: TVA sur Biens et Services à 3.8% |


  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 3.8% invest
    And having:
    | name                 | value                                           |
    | account_collected_id | by code: 445662 and company_id.name: Helom SARL |
    | account_paid_id      | by code: 445662 and company_id.name: Helom SARL |


  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 8.0% invest.
    And having:
    | name                 | value                                           |
    | account_collected_id | by code: 445662 and company_id.name: Helom SARL |
    | account_paid_id      | by code: 445662 and company_id.name: Helom SARL |

  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 2.5%
    And having:
    | name                  | value             |
    | account_collected_id  | by code: 445713   |
    | account_paid_id       | by code: 445713   |


  @helom_taxes_accounts_relations
  Scenario: RECREATED LINK ACCOUNTS-TAXES AFTER CUSTOM CoA IMPORT

    Given I need a "account.tax" with description: 3.8%
    And having:
    | name                  | value             |
    | account_collected_id  | by code: 445712   |
    | account_paid_id       | by code: 445712   |
