@debonix  @migration  @accounting

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | account_tid_reconcile              |
      | currency_rate_update               |
      | l10n_fr_profile                    |
      | account_invoice_reference          |
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

  #@accounts
  #Scenario Outline: Create the accounts (explain)
    #Given I need a "account.account" with oid: <account_oid>
    #And having:
      #| name       | value                                        |
      #| name       | <name>                                       |
      #| code       | <code>                                       |
      #| parent_id  | by name: Valeur à l'encaissement             |
      #| type       | liquidity                                    |
      #| user_type  | by oid: account.data_account_type_receivable |
      #| reconcile  | true                                         |
      #| company_id | by oid: base.main_company                    |
      #| active     | true                                         |
      #| type       | receivable                                   |

    #Examples:
      #| account_oid              | name                                    | code   |
      #| scenario.account_auto_transation | Attente Confirmation Office de Paiement | 511003 |
      #| scenario.account_conf_transation | Attente Virement Office de Paiement     | 511004 |

  ## TODO check if this will work with code
  #Scenario: Edit paypal account
    #Given I find or create a "account.account" with code: 512240
    #And having:
      #| name       | value                                   |
      #| name       | Paypal                                  |
      #| parent_id  | by name: Banques                        |
      #| type       | liquidity                               |
      #| user_type  | by oid: account.data_account_type_asset |
      #| reconcile  | false                                   |
      #| company_id | by oid: base.main_company               |
      #| active     | true                                    |

###############################################################


  # ------------------------------------------------------------------------------------------
  @finance_flow_current
  Scenario: Delete e-commerce payment type
  # ------------------------------------------------------------------------------------------

    Given I delete the "base.sale.payment.type" with name "checkmo;cashondelivery"
    And I delete the "base.sale.payment.type" with name "ccsave;free;googlecheckout;paypayl_express;paybox_system;paypal_standard;servired_standard;bbva;cofidis"

    And I delete the "base.sale.payment.type" with name "checkmo"
    And I delete the "base.sale.payment.type" with name "ccsave;free;googlecheckout;paypayl_express;paybox_system;paypal_standard;servired_standard;bbva;cofidis"
    And I delete the "base.sale.payment.type" with name "atos_standard"
    And I delete the "base.sale.payment.type" with name "cybermut_payment"
    And I delete the "base.sale.payment.type" with name "mjoney3x; mjoney4x"
    And I delete the "base.sale.payment.type" with name "bankcr"
    And I delete the "base.sale.payment.type" with name "receiveandpay_cb; receiveandpay_cr"
    And I delete the "base.sale.payment.type" with name "amazon;mediacadeaux"
    And I delete the "base.sale.payment.type" with name "m2epropayment"
    And I delete the "base.sale.payment.type" with name "pixmania"
    And I delete the "base.sale.payment.type" with name "partenaire"
    And I delete the "base.sale.payment.type" with name "chequethreetimes"
    And I delete the "base.sale.payment.type" with name "chequefivetimes"
    And I delete the "base.sale.payment.type" with name "cashondelivery"
    And I delete the "base.sale.payment.type" with name "bank;bankpayment"
    And I delete the "base.sale.payment.type" with name "oney_oney3x;mjoney3x"
    And I delete the "base.sale.payment.type" with name "atos_several;vads"
    And I delete the "base.sale.payment.type" with name "outilmania"
    And I delete the "base.sale.payment.type" with name "vadsmulti"
    And I delete the "base.sale.payment.type" with name "rdc"
    And I delete the "base.sale.payment.type" with name "purchaseorder;MarketPlacePaymentMethod"

  @finance_flow_current
  Scenario: Configure e-commerce payment type
    Given I define the global configuration of the payment types with values:
      | key                          | value      |
      | picking_policy               | 'one'      |
      | invoice_quantity             | 'order'    |
      | order_policy                 | 'postpaid' |
      | validate_order               | false      |
      | check_if_paid                | false      |
      | create_invoice               | false      |
      | validate_invoice             | false      |
      | validate_picking             | false      |
      | validate_manufacturing_order | false      |
      | invoice_date_is_order_date   | true       |
      | days_before_order_cancel     | 30         |
      | validate_payment             | false      |
      | is_auto_reconcile            | false      |
      | payment_term_id              | false      |
      | journal_id                   | false      |
      | allow_magento_manual_invoice | false      |
    And I define a "AUTOMATIC 1 PAYMENT" payment type pattern with values:
      | key               | value |
      | validate_order    | true  |
      | check_if_paid     | true  |
      | create_invoice    | true  |
      | validate_invoice  | true  |
      | validate_payment  | true  |
      | is_auto_reconcile | true  |
    And I define a "AUTOMATIC NO ORDER 1 PAYMENT" payment type pattern with values:
      | key               | value |
      | validate_order    | false |
      | check_if_paid     | true  |
      | create_invoice    | true  |
      | validate_invoice  | true  |
      | validate_payment  | true  |
      | is_auto_reconcile | true  |
    And I define a "MANUAL X PAYMENT" payment type pattern with values:
      | key               | value |
      | validate_order    | false |
      | check_if_paid     | false |
      | create_invoice    | true  |
      | validate_invoice  | true  |
      | validate_payment  | false |
      | is_auto_reconcile | false |


    # ------------------------------------------------------------------------------------------
    # Paiement 1x par office tier
    # ------------------------------------------------------------------------------------------
    # Template
    Given I define a "PATTERN_VIRBC" payment type pattern with values:
      | key             | value                                          |
      | journal_id      | name 'Attente Confirmation Office de Paiement' |
      | payment_term_id | name 'VIRBC'                                   |
    And the other values of "PATTERN_VIRBC" pattern are those of "AUTOMATIC 1 PAYMENT"
    Given I define a "PATTERN_CB" payment type pattern with values:
      | key             | value                                          |
      | journal_id      | name 'Attente Confirmation Office de Paiement' |
      | payment_term_id | name 'CBCOM'                                   |
    And the other values of "PATTERN_CB" pattern are those of "AUTOMATIC 1 PAYMENT"
    Given I define a "PATTERN_RECEIVE_N_PAY" payment type pattern with values:
      | key             | value                                          |
      | journal_id      | name 'Attente Confirmation Office de Paiement' |
      | payment_term_id | name 'CBCOM'                                   |
    And the other values of "PATTERN_RECEIVE_N_PAY" pattern are those of "AUTOMATIC NO ORDER 1 PAYMENT"

    Given I find or create a "account.statement.profile" with name: Paypal and oid: scenario.profile_paypal
    And having:
      | name                  | value                                        |
      | partner_id            | by name: paypal                              |
      | journal_id            | by name: PayPal Banque                       |
      | commission_account_id | by name: Commissions et courtages sur ventes |
      | balance_check         | true                                         |
      | force_partner_on_bank | true                                         |
      | launch_import_completion | true                                      |
      | import_type           | generic_csvxls_so                            |
    Then I want to use the following payment codes with the "PATTERN_VIRBC" payment type with reference "scenario.paypal_standard":
      | Payment Code |
      | paypal_standard |

    Given I find or create a "res.partner" with name: Pixmania and oid: scenario.part_pixmania
    And having:
      | name          | value                                  |
      | ref           | pixmania                               |
      | property_account_receivable   | by oid: scenario.conf_transaction |
    Given I find or create a "account.statement.profile" with name: Pixmania and oid: scenario.config_pixmania
    And having:
      | name                  | value                                            |
      | partner_id            | by name: Pixmania                                |
      | journal_id            | by name: Attente Virement Office de Paiement     |
      | commission_account_id | by name: Commissions et courtages sur ventes     |
      | receivable_account_id | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank | true                                             |
      | import_type           | generic_csvxls_so                            |
      | launch_import_completion | true                                      |

    Then I want to use the following payment codes with the "PATTERN_VIRBC" payment type with reference "scenario.pixmania":
      | Payment Code |
      | pixmania     |

    Given I find or create a "account.statement.profile" with name: Amazon and oid: scenario.config_amazon
    And having:
      | name                     | value                                            |
      | partner_id               | by name: AMAZON                                  |
      | journal_id               | by name: Attente Virement Office de Paiement     |
      | commission_account_id    | by name: Commissions et courtages sur ventes     |
      | receivable_account_id    | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank    | true                                             |
      | import_type              | generic_csvxls_transaction                       |
      | launch_import_completion | true                                             |

    Then I want to use the following payment codes with the "PATTERN_VIRBC" payment type with reference "scenario.amazon":
      | Payment Code |
      | amazon       |

    Given I find or create a "account.statement.profile" with name: Mediacadeau and oid: scenario.config_mediacadeaux
    And having:
      | name                     | value                                            |
      | partner_id               | by name: MEDIACADEAUX                            |
      | journal_id               | by name: Attente Virement Office de Paiement     |
      | commission_account_id    | by name: Commissions et courtages sur ventes     |
      | receivable_account_id    | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank    | true                                             |
      | import_type              | generic_csvxls_so                                |
      | launch_import_completion | true                                             |

    Then I want to use the following payment codes with the "PATTERN_VIRBC" payment type with reference "scenario.mediacadeaux":
      | Payment Code |
      | mediacadeaux |

    Given I find or create a "account.statement.profile" with name: VADS (PAYZEN) and oid: scenario.config_vads
    And having:
      | name                     | value                                            |
      | partner_id               | by name: PAYZEN                                  |
      | journal_id               | by name: Attente Virement Office de Paiement     |
      | commission_account_id    | by name: Commissions et courtages sur ventes     |
      | receivable_account_id    | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank    | true                                             |
      | import_type              | generic_csvxls_so                                |
      | launch_import_completion | true                                             |

    Then I want to use the following payment codes with the "PATTERN_CB" payment type with reference "scenario.vads":
      | Payment Code |
      | vads         |
# ------------------------------------------------------------------------------------------
    Given I find or create a "res.partner" with name: Sofinco and oid: scenario.part_sofinco
    And having:
      | name                        | value                             |
      | ref                         | sofinco                           |
      | property_account_receivable | by oid: scenario.conf_transaction |
    Given I find or create a "account.statement.profile" with name: Sofinco CB and oid: scenario.config_receiveandpay_cb
    And having:
      | name                     | value                                            |
      | partner_id               | by name: Sofinco                                 |
      | journal_id               | by name: Attente Virement Office de Paiement     |
      | commission_account_id    | by name: Commissions et courtages sur ventes     |
      | receivable_account_id    | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank    | true                                             |
      | import_type              | generic_csvxls_so                                |
      | launch_import_completion | true                                             |

    Then I want to use the following payment codes with the "PATTERN_RECEIVE_N_PAY" payment type with reference "scenario.receiveandpay_cb":
      | Payment Code |
      | receiveandpay_cb |

    Given I find or create a "account.statement.profile" with name: Sofinco CR and oid: scenario.config_receiveandpay_cr
    And having:
      | name                     | value                                            |
      | partner_id               | by name: Sofinco                                 |
      | journal_id               | by name: Attente Virement Office de Paiement     |
      | commission_account_id    | by name: Commissions et courtages sur ventes     |
      | receivable_account_id    | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank    | true                                             |
      | import_type              | generic_csvxls_so                                |
      | launch_import_completion | true                                             |

    Then I want to use the following payment codes with the "PATTERN_RECEIVE_N_PAY" payment type with reference "scenario.receiveandpay_cr":
      | Payment Code |
      | receiveandpay_cr |

# ------------------------------------------------------------------------------------------

    Given I find or create a "account.statement.profile" with name: Rue Du Commerce and oid: scenario.config_rdc
    And having:
      | name                     | value                                            |
      | partner_id               | by name: RUE DU COMMERCE                         |
      | journal_id               | by name: Attente Virement Office de Paiement     |
      | commission_account_id    | by name: Commissions et courtages sur ventes     |
      | receivable_account_id    | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank    | true                                             |
      | import_type              | generic_csvxls_so                                |
      | launch_import_completion | true                                             |

    Then I want to use the following payment codes with the "PATTERN_VIRBC" payment type with reference "scenario.rdc":
      | Payment Code |
      | rdc          |

    Given I find or create a "res.partner" with name: OutilMania and oid: scenario.part_outilmania
    And having:
      | name | value      |
      | ref  | outilmania |
      | property_account_receivable   | by oid: scenario.conf_transaction |
    Given I find or create a "account.statement.profile" with name: OutilMania and oid: scenario.config_outilmania
    And having:
      | name                     | value                                            |
      | partner_id               | by name: OutilMania                              |
      | journal_id               | by name: Attente Virement Office de Paiement     |
      | commission_account_id    | by name: Commissions et courtages sur ventes     |
      | receivable_account_id    | by name: Attente Confirmation Office de Paiement |
      | force_partner_on_bank    | true                                             |
      | import_type              | generic_csvxls_so                                |
      | launch_import_completion | true                                             |

    Then I want to use the following payment codes with the "PATTERN_VIRBC" payment type with reference "scenario.outilmania":
      | Payment Code |
      | outilmania   |

    Given I find or create a "res.partner" with name: EBay and oid: scenario.part_ebay
    And having:
      | name | value |
      | ref  | ebay  |
      | property_account_receivable   | by oid: scenario.conf_transaction |
    Given I find or create a "account.statement.profile" with name: M2E Pro and oid: scenario.config_m2epropayment
    And having:
      | name                     | value                                        |
      | partner_id               | by name: paypal                              |
      | journal_id               | by name: PayPal Banque                       |
      | commission_account_id    | by name: Commissions et courtages sur ventes |
      | force_partner_on_bank    | true                                         |
      | balance_check            | true                                         |
      | import_type              | generic_csvxls_transaction                   |
      | launch_import_completion | true                                         |

    Then I want to use the following payment codes with the "PATTERN_VIRBC" payment type with reference "scenario.m2epropayment":
      | Payment Code  |
      | m2epropayment |


    # ------------------------------------------------------------------------------------------
    # Paiement multiple autofinancé (2e flux)
    # ------------------------------------------------------------------------------------------
    Given I define a "VADS MULTI" payment type pattern with values:
      | key             | value                                          |
      | payment_term_id | name 'CB3X'                                    |
      | journal_id      | name 'Attente Confirmation Office de Paiement' |
    And the other values of "VADS MULTI" pattern are those of "AUTOMATIC 1 PAYMENT"
    Then I want to use the following payment codes with the "VADS MULTI" payment type with reference "scenario.vadsmulti":
      | Payment Code |
      | vadsmulti    |

  @finance_flow_current
  Scenario: Configure and correct journals and shop
    Given I find or create a "account.journal" with code: VTE
    And having:
      | name                      | value                                                            |
      | default_credit_account_id | by name: Clients - Ventes de biens ou de prestations de services |
      | default_debit_account_id  | by name: Clients - Ventes de biens ou de prestations de services |
      | analytic_journal_id       | by name: VENTES                                                  |
    And I find or create a "sale.shop" with name: Main Website Store
    And having:
      | name         | value        |
      | sale_journal | by code: VTE |


  # ------------------------------------------------------------------------------------------
  # Paiement multiple autofinancé (2e flux)
  # ------------------------------------------------------------------------------------------

  @finance_flow_current
  Scenario: Configure reconcile rules
  Given I find or create a "account.easy.reconcile" with name: 411 - Clients and oid: scenario.easy_reconcile_411
  And having:
    | name    | value                                                            |
    | account | by name: Clients - Ventes de biens ou de prestations de services |

  Given I find or create a "account.easy.reconcile.method" with oid: scenario.method_reconcile_411
  And having:
    | name              | value                                         |
    | name              | easy.reconcile.advanced.tid                   |
    | sequence          | 10                                            |
    | task_id           | by oid: scenario.easy_reconcile_411           |
    | write_off         | 0.05                                          |
    | account_lost_id   | by name: Charges diverses de gestion courante |
    | account_profit_id | by name: Produits divers de gestion courante  |
    | journal_id        | by name: Opérations diverses                  |
    | date_base_on      | end_period_last_credit                        |

  Given I find or create a "account.easy.reconcile" with name: 511003 - Attente Confirmation Office de Paiement and oid: scenario.easy_reconcile_511003
  And having:
    | name    | value                                            |
    | account | by name: Attente Confirmation Office de Paiement |

  Given I find or create a "account.easy.reconcile.method" with oid: scenario.method_reconcile_511003
  And having:
    | name              | value                                         |
    | name              | easy.reconcile.advanced.tid                   |
    | sequence          | 10                                            |
    | task_id           | by oid: scenario.easy_reconcile_511003        |
    | write_off         | 0.05                                          |
    | account_lost_id   | by name: Charges diverses de gestion courante |
    | account_profit_id | by name: Produits divers de gestion courante  |
    | journal_id        | by name: Opérations diverses                  |
    | date_base_on      | end_period_last_credit                        |

  Given I find or create a "account.easy.reconcile" with name: 511004 - Attente Virement Office de Paiement and oid: scenario.easy_reconcile_511004
  And having:
    | name    | value                                        |
    | account | by name: Attente Virement Office de Paiement |

  Given I find or create a "account.easy.reconcile.method" with oid: scenario.method_reconcile_511004
  And having:
    | name              | value                                         |
    | name              | easy.reconcile.advanced.tid                   |
    | sequence          | 10                                            |
    | task_id           | by oid: scenario.easy_reconcile_511004        |
    | write_off         | 0.05                                          |
    | account_lost_id   | by name: Charges diverses de gestion courante |
    | account_profit_id | by name: Produits divers de gestion courante  |
    | journal_id        | by name: Opérations diverses                  |
    | date_base_on      | end_period_last_credit                        |

# ------------------------------------------------------------------------------------
# Completion Rule
# ------------------------------------------------------------------------------------



    @finance_flow_current
    Scenario: Configure the sequence of the completion rules
    Given I find or create a "account.statement.completion.rule" with name: Match from line reference (based on SO number with or without mag prefix)
    And having:
      | name              | value                                       |
      | sequence          | 30                                          |
    Given I find or create a "account.statement.completion.rule" with name: Match from line reference (based on transaction ID)
    And having:
      | name     | value |
      | sequence | 50    |

    @finance_flow_current
    Scenario: Configure the bank partner properties
    Given I find or create a "res.partner" with name: paypal
    And having:
      | name                        | value                             |
      | property_account_receivable | by oid: scenario.conf_transaction |
    Given I find or create a "res.partner" with name: AMAZON
    And having:
      | name                        | value                             |
      | property_account_receivable | by oid: scenario.conf_transaction |
    Given I find or create a "res.partner" with name: MEDIACADEAUX
    And having:
      | name                        | value                             |
      | property_account_receivable | by oid: scenario.conf_transaction |
    Given I find or create a "res.partner" with name: PAYZEN
    And having:
      | name                        | value                             |
      | property_account_receivable | by oid: scenario.conf_transaction |
    Given I find or create a "res.partner" with name: RUE DU COMMERCE
    And having:
      | name                        | value                             |
      | property_account_receivable | by oid: scenario.conf_transaction |

    @finance_flow_current
    Scenario: Change all journal type from cash to bank
    Given I execute following sql:
    """
        UPDATE account_journal SET type = 'bank' WHERE type = 'cash';
    """

    @finance_flow_current
    Scenario: Change the caisse journal to type cash
    Given I execute following sql:
    """
        UPDATE account_journal SET type = 'cash' WHERE name = 'Caisse';
    """

    @current
    @finance_flow_current
    Scenario: Forbid to use another periode  than the coresponding date in all journals
    Given I execute following sql:
    """
        UPDATE account_journal SET allow_date = 't';
    """

  @finance_flow_current
  Scenario: rebind sales order on the new base sale payment types
    Given I execute following sql:
    """
    UPDATE sale_order
    SET base_payment_type_id = (SELECT id
                                FROM base_sale_payment_type
                                WHERE name = sale_order.ext_payment_method)
    WHERE base_payment_type_id NOT IN (SELECT id FROM base_sale_payment_type);
    """
