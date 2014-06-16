@debonix  @migration  @bank_profile

Feature: BANK PROFILES

  # ------------------------------------------------------------------------------------------
  # Relevés bancaires
  # ------------------------------------------------------------------------------------------
  Scenario Outline: BANK PROFILE FOR DEBONIX
    Given I am configuring the company with ref "base.main_company"
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
      | name                  | value                     |
      | name                  | <name>                    |
      | journal_id            | by name: <journal>        |
      | commission_account_id | by code: 622200           |
      | balance_check         | 1                         |
      | import_type           | generic_csvxls_so         |
      | company_id            | by oid: base.main_company |
    And with following rules
      | name                                                                  |
      | Match from line reference (based on Invoice number)                   |
      | Match from line reference (based on Invoice Supplier number)          |
      | Match from line label (based on partner field 'Bank Statement Label') |
      | Match from line label (based on partner name)                         |

    Examples: Bank profiles for debonix
      | oid                                  | name                 | journal                |
      | scenario.profile_credit_mutuel       | Crédit Mutuel        | Crédit Mutuel EUR 3    |
      | scenario.profile_banque_populaire    | Banque Populaire     | Banque Populaire       |
      | scenario.profile_credit_lyonnais     | Crédit Lyonnnais     | Crédit Lyonnais EUR    |
      | scenario.profile_credit_lyonnais_2   | Crédit Lyonnnais 2   | Crédit Lyonnais 466338 |
      | scenario.profile_cic                 | CIC                  | CIC                    |
      | scenario.profile_credit_lyonnais_USD | Crédit Lyonnnais USD | Crédit Lyonnais USD    |
      | scenario.profile_caisse              | Caisse               | Caisse                 |

  Scenario Outline: BANK PROFILE FOR DEBONIX
    Given I am configuring the company with ref "base.main_company"
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
      | name                  | value                     |
      | name                  | <name>                    |
      | journal_id            | by name: <journal>        |
      | commission_account_id | by code: 622200           |
      | balance_check         | 1                         |
      | import_type           | generic_csvxls_so         |
      | company_id            | by oid: base.main_company |
    And with following rules
      | name                                           |
      | Match from Sales Order using transaction ID     |
      | Match from line reference (based on SO number) |
      | Match from Invoice using transaction ID        |

    Examples: Paypal Bank profiles for debonix
      | oid                      | name     | journal       |
      | scenario.profile_paypal  | Paypal   | PAYPAL_V5_OLD |
      | scenario.profile_paypal2 | Paypal 2 | PAYZEN BP 2   |

  # ------------------------------------------------------------------------------------------
  # Imports de payement
  # ------------------------------------------------------------------------------------------
  Scenario Outline: BANK PROFILE FOR PAYMENT IMPORT
    Given I am configuring the company with ref "base.main_company"
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
      | name                  | value                     |
      | name                  | <name>                    |
      | journal_id            | by code: <journal>        |
      | commission_account_id | by code: 622200           |
      | receivable_account_id | by code: 411000           |
      | balance_check         | 0                         |
      | import_type           | generic_csvxls_so         |
      | company_id            | by oid: base.main_company |
    And with following rules
      | name                                           |
      | Match from Sales Order using transaction ID     |
      | Match from line reference (based on SO number) |
      | Match from Invoice using transaction ID        |

    Examples: Bank import for Debonix payments
      | oid                                         | name                                  | journal |
      | scenario.profile_import_check               | Remise de Chèques (Clients)           | RCHQ    |
      | scenario.profile_import_cb_banque_populaire | Import Carte bancaire Banque Pop      | CB_BP   |
      | scenario.profile_import_cb_credit_lyonnais  | Import Carte bancaire Crédit Lyonnais | CB_CL   |
      | scenario.profile_import_cb_credit_mutuel    | Import Carte bancaire Crédit Mutuel   | CB_CM   |
      | scenario.profile_import_outilmania          | Import Outilmania                     | outil   |
      | scenario.profile_import_priceminister       | Import PriceMinister                  | PRICE   |
      | scenario.profile_import_pixmania            | Import Pixmania                       | pix     |
      | scenario.profile_import_amazon              | Import Virement Amazon                | amazon  |
      | scenario.profile_import_banque_accord       | Import Banque Accord                  | accor   |
      | scenario.profile_import_rdc                 | Import Virement Rue Du Commerce       | RDC     |
      | scenario.profile_import_sofinco             | Import Virement Sofinco               | sofin   |
