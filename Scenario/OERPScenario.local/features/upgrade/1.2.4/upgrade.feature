# -*- coding: utf-8 -*-
@upgrade_from_1.2.3 @debonix

Feature: upgrade to 1.2.4

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                 |
      | debonix_purchase_edi |
      | specific_fct         |
    Then my modules should have been installed and models reloaded

  Scenario: update SOGEDESCA partner for new EDI functionality
    Given I execute the SQL commands
    """
    UPDATE res_partner
    SET edifact_message = True,
        code_filiale = 'PLN',
        siret_filiale = '52789590800012',
        code_agence = '928',
        siret_agence = '52789590800012',
        compte_debonix = '0000175000'
    WHERE name = 'SOGEDESCA';
    """

    Given I set the version of the instance to "1.2.4"
