@debonix  @migration  @document_settings

Feature: Ensure that document configuration is correct


  Scenario: Configure the directories
    Given I need a "document.directory" with name: import_tracking and oid: scenario.import_tracking
    And having:
      | name        | value      |
