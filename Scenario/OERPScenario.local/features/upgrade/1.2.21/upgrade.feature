# -*- coding: utf-8 -*-
@upgrade_to_1.2.21 @debonix

Feature: upgrade to 1.2.21

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                 |
      | debonix_supplier_invoice_edi                 |
    Then my modules should have been installed and models reloaded

    Given I load the data file "supplier_invoice_edi/res_company.csv" into the model "res.company"

    Given I set the version of the instance to "1.2.21"
