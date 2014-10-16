@debonix @migration @merge_partners

Feature: Merge partners that give problems with Intrastat

  Scenario: Merge problematic suppliers
    Given I find a "res.partner" with name "FESTOOL"
    Then I merge them
