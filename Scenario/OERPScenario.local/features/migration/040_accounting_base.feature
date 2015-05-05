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
    -- correct data: moves that were 'sale' but in the old refund journal should be moved to the sale journal
    UPDATE account_move_line SET journal_id = 2 WHERE journal_id = 16;
    UPDATE account_move SET journal_id = 2 WHERE journal_id = 16;
    UPDATE account_journal SET name = 'Journal d''avoir sur achats (ancien)', code = 'AACH-X', active = false
    WHERE id = 17;
    -- correct data: moves that were 'purchase' but in the old refund journal should be moved to the purchase journal
    UPDATE account_move_line SET journal_id = 3 WHERE journal_id = 17;
    UPDATE account_move SET journal_id = 3 WHERE journal_id = 17;
    -- merge journals
    UPDATE account_journal SET name = 'Journal d''avoir sur ventes', code = 'AVTE' WHERE code = 'AVTE-R';
    UPDATE account_move_line SET journal_id = (SELECT id FROM account_journal WHERE code = 'AVTE') WHERE journal_id = (SELECT id FROM account_journal WHERE code = 'VTE-R');
    UPDATE account_move SET journal_id = (SELECT id FROM account_journal WHERE code = 'AVTE') WHERE journal_id = (SELECT id FROM account_journal WHERE code = 'VTE-R');
    UPDATE account_journal SET active = false WHERE code = 'VTE-R';

    UPDATE account_journal SET name = 'Journal d''avoir sur achats', code = 'AACH' WHERE code = 'AACH-R';
    UPDATE account_move_line SET journal_id = (SELECT id FROM account_journal WHERE code = 'AACH') WHERE journal_id = (SELECT id FROM account_journal WHERE code = 'ACH-R');
    UPDATE account_move SET journal_id = (SELECT id FROM account_journal WHERE code = 'AACH') WHERE journal_id = (SELECT id FROM account_journal WHERE code = 'ACH-R');
    UPDATE account_journal SET active = false WHERE code = 'ACH-R';
    """

  @analytic_journal
  Scenario: deactivate the default sale analytic journal
    Given I find a possibly inactive "account.analytic.journal" with oid: account.analytic_journal_sale
    And having:
      | key    | value |
      | active | false |

  @analytic_journal
  Scenario: create missing analytic journals
    Given I need an "account.analytic.journal" with oid: scenario.anl_journal_purchase
    And having:
      | key  | value    |
      | name | ACHATS   |
      | code | ACHAT    |
      | type | purchase |
    Given I need an "account.analytic.journal" with oid: scenario.anl_journal_various
    And having:
      | key  | value   |
      | name | DIVERS  |
      | code | DIVERS  |
      | type | general |

  @journal
  Scenario Outline: Link journals to analytic journals
    Given I find an "account.journal" with code: <code>
    And having:
      | key                 | value              |
      | analytic_journal_id | <analytic_journal> |

  Examples: analytic journals
      | code | analytic_journal                      |
      | ACH  | by oid: scenario.anl_journal_purchase |
      | AACH | by oid: scenario.anl_journal_purchase |
      | VTE  | by code: COMAG                        |
      | AVTE | by code: COMAG                        |

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
      | C''DISCOUNT   | CDISC    |

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
      | CDISC | Import C''DISCOUNT                    |


  @duplicate_taxes
  Scenario: Remove the duplicate taxes on products
    Given I execute the SQL commands
    """
    DELETE FROM product_taxes_rel AS ptrl1
    USING product_taxes_rel AS ptrl2
    WHERE ptrl1.prod_id = ptrl2.prod_id
    AND ptrl1.tax_id = ptrl2.tax_id AND ptrl1.ctid = (SELECT MAX(ptrl3.ctid)
                                                      FROM product_taxes_rel AS ptrl3
                                                      WHERE ptrl3.prod_id = ptrl1.prod_id
                                                      GROUP BY ptrl3.prod_id, ptrl3.tax_id
                                                      HAVING COUNT(*) > 1);


    DELETE FROM product_supplier_taxes_rel AS ptrlX
    USING product_supplier_taxes_rel AS ptrl2
    WHERE ptrlX.prod_id = ptrl2.prod_id
    AND ptrlX.tax_id = ptrl2.tax_id
    AND ptrlX.ctid = (SELECT MAX(ptrl3.ctid)
                      FROM product_supplier_taxes_rel AS ptrl3
                      WHERE ptrl3.prod_id = ptrlX.prod_id
                      GROUP BY ptrl3.prod_id, ptrl3.tax_id
                      HAVING COUNT(*) > 1);
    """