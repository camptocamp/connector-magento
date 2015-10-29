# -*- coding: utf-8 -*-
@upgrade_magento_enterprise @debonix

Feature: upgrade to Magento Enterprise

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                 |
      | connector                            |
      | magentoerpconnect                    |
      | server_env_magentoerpconnect         |
      | specific_magento                     |
    Then my modules should have been installed and models reloaded

