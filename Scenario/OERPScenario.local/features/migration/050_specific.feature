@debonix  @migration  @specific

Feature: install and migrate the picking priorities modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                               |
      | specific_fct                       |
      | delivery_carrier_file_chronopost   |
    Then my modules should have been installed and models reloaded

  Scenario: Delete the Update AVCO cron, no longer needed
    Given I execute the SQL commands
    """
    DELETE FROM ir_cron WHERE id = 23;
    """
