@debonix  @migration  @accounting

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | account_tid_reconcile              |
      | currency_rate_update               |
    Then my modules should have been installed and models reloaded

  @journal_type
  Scenario: The journal have new types
    Given I find an "account.journal" with code: AVTE
    And having:
      | name | value       |
      | type | sale_refund |
    Given I find an "account.journal" with code: AACH
    And having:
      | name | value           |
      | type | purchase_refund |
    Given I find an "account.journal" with code: ACH
    And having:
      | name | value    |
      | type | purchase |

  @bank_journals
  Scenario Outline: Reduce journal code to 5 chars
    Given I execute the SQL commands
    """
        UPDATE account_journal SET code = '<new_code>' WHERE code = '<code>';
    """
  Examples: Bank Journals
      | code          | new_code |
      | outilmania    | outil    |
      | PRICEMINISTER | PRICE    |
      | amazon        | amazo    |
      | accord        | accor    |
      | sofinco       | sofin    |
      | accord        | accor    |
      | sofinco       | sofin    |

  @bank_journals
  Scenario Outline: Rename all import journals adding 'Import'
    Given I need an "account.journal" with code: <code>
    And having:
      | key  | value  |
      | name | <name> |

  Examples: Bank Journals
      | code  | name                                  |
      | CB_BP | Import Carte bancaire Banque Pop      |
      | CB_CL | Import Carte bancaire Crédit Lyonnais |
      | CB_CM | Import Carte bancaire Crédit Mutuel   |
      #? | FRANF  | Import Franfinance              |
      | outil | Import Outilmania                     |
      | PRICE | Import PriceMinister                  |
      | pix   | Import Pixmania                       |
      | amazo | Import Virement Amazon                |
      | accor | Import Virement Banque Accord         |
      | RDC   | Import Virement Rue Du Commerce       |
      | sofin | Import Virement Sofinco               |

