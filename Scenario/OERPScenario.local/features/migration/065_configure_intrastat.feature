@debonix @migration @configure_intrastat

Feature: configure Intrastat in the company

  Scenario: configure Intrastat parameters
      Given I need a "res.company" with oid: base.main_company
      And having:
         | name                    | value    |
         | export_obligation_level |          |
         | import_obligation_level | detailed |

