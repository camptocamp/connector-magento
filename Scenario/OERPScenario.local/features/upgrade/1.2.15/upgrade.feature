# -*- coding: utf-8 -*-
@upgrade_to_1.2.15 @debonix

Feature: upgrade to 1.2.15

  Scenario: assign xml_id to crm categ
    Given I execute the SQL commands
    """
        INSERT INTO ir_model_data (
          noupdate,
          name,
          module,
          model,
          res_id
        )
        VALUES (
          false,
          'categ_claim_pln_incident',
          'debonix_purchase_edi',
          'crm.case.categ',
          70
        );
    """

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                    |
      | specific_fct            |
      | toolstream_purchase_edi |
      | debonix_purchase_edi    |
      | stockit_synchro         |
    Then my modules should have been installed and models reloaded

    Given I set the version of the instance to "1.2.15"
