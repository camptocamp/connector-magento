# -*- coding: utf-8 -*-
@upgrade_to_1.2.21 @debonix

Feature: upgrade to 1.2.21

  Scenario: install supplier invoice edi module
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                 |
      | specific_fct                         |
      | debonix_supplier_invoice_edi         |
    Then my modules should have been installed and models reloaded

  Scenario: define supplier invoice EDI values for company debonix
    Given I load the data file "supplier_invoice_edi/res_company.csv" into the model "res.company"
    Given I execute the SQL commands
    """
    UPDATE res_company
    SET edifact_supplier_invoice_partner_id = (
        SELECT p.id
        FROM res_partner p
        WHERE p.name = 'SOGEDESCA')
    WHERE name = 'Debonix France SAS';
    """

  Scenario: upgrade application version
    Given I set the version of the instance to "1.2.21"
