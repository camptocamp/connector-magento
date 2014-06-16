@debonix  @migration  @accounting

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | account_tid_reconcile              |
      | currency_rate_update               |
      | debonix_accounting_profile         |
      | account_invoice_reference          |
    Then my modules should have been installed and models reloaded

  @journal
  Scenario: openerp migration created new journal for the refunds and moved the refund move lines in them (and left some move lines which were in the wrong journal in the old journals)
    Given I execute the SQL commands
    """
    UPDATE account_journal SET name = 'Journal d''avoir sur ventes (ancien)', code = 'AVTE-X', active = false
    WHERE id = 16;
    UPDATE account_journal SET name = 'Journal d''avoir sur achats (ancien)', code = 'AACH-X', active = false
    WHERE id = 17;
    UPDATE account_journal SET name = 'Journal d''avoir sur ventes', code = 'AVTE' WHERE code = 'AVTE-R';
    UPDATE account_journal SET name = 'Journal d''avoir sur achats', code = 'AACH' WHERE code = 'AACH-R';
    """

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
      | FRANFINANCE   | FRANF    |

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
      | outil | Import Outilmania                     |
      | PRICE | Import PriceMinister                  |
      | pix   | Import Pixmania                       |
      | amazo | Import Virement Amazon                |
      | accor | Import Virement Banque Accord         |
      | RDC   | Import Virement Rue Du Commerce       |
      | sofin | Import Virement Sofinco               |
      | FRANF | Import Franfinance                    |

