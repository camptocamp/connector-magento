@helom_init @helom_init_crons @upgrade_from_1.0.4


Feature: set cron to support multicompany setup

Scenario: Setup cron "Automatic Workflow Job"
    Given I reassign cron "Automatic Workflow Job" from user "admin" to "admin_fr"
    And I duplicate cron "Automatic Workflow Job" and assign it to user "admin_ch" with a delay of "120" seconds

Scenario: Setup cron "Check Action Rules"
    Given I reassign cron "Check Action Rules" from user "admin" to "admin_fr"
    And I duplicate cron "Check Action Rules" and assign it to user "admin_ch" with a delay of "120" seconds

Scenario: Setup cron "Check Availability of Delivery Orders"
    Given I reassign cron "Check Availability of Delivery Orders" from user "admin" to "admin_fr"

Scenario: Setup cron "Check cases rules"
    Given I reassign cron "Check cases rules" from user "admin" to "admin_fr"
    And I duplicate cron "Check cases rules" and assign it to user "admin_ch" with a delay of "120" seconds

Scenario: Setup cron "Do Automatic Reconciliations"
    Given I reassign cron "Do Automatic Reconciliations" from user "admin" to "admin_fr"
    And I duplicate cron "Do Automatic Reconciliations" and assign it to user "admin_ch" with a delay of "120" seconds

Scenario: Setup cron "Magento -  Import Product Categories"
    Given I reassign cron "Magento -  Import Product Categories" from user "admin" to "admin_fr"

Scenario: Setup cron "Magento -  Import Products"
    Given I reassign cron "Magento -  Import Products" from user "admin" to "admin_fr"

Scenario: Setup cron "Magento -  Update Product Cost"
    Given I reassign cron "Magento -  Update Product Cost" from user "admin" to "admin_fr"

Scenario: Setup cron "Magento -  Update Stock Quantities"
    Given I reassign cron "Magento -  Update Stock Quantities" from user "admin" to "admin_fr"

Scenario: Setup cron "Magento - Import Sales Orders"
    Given I reassign cron "Magento - Import Sales Orders" from user "admin" to "admin_fr"

Scenario: Setup cron "Run Event Reminder"
    Given I reassign cron "Run Event Reminder" from user "admin" to "admin_fr"
    And I duplicate cron "Run Event Reminder" and assign it to user "admin_ch" with a delay of "120" seconds

Scenario: Setup cron "Stockit Export In Pickings"
    Given I reassign cron "Stockit Export In Pickings" from user "admin" to "admin_fr"

Scenario: Setup cron "Stockit Export Out Pickings"
    Given I reassign cron "Stockit Export Out Pickings" from user "admin" to "admin_fr"

Scenario: Setup cron "Stockit Import Ingoing picking"
    Given I reassign cron "Stockit Import Ingoing picking" from user "admin" to "admin_fr"

Scenario: Setup cron "Stockit Import Inventory"
    Given I reassign cron "Stockit Import Inventory" from user "admin" to "admin_fr"

Scenario: Setup cron "Test Draft Orders"
    Given I reassign cron "Test Draft Orders" from user "admin" to "admin_fr"
    And I duplicate cron "Test Draft Orders" and assign it to user "admin_ch" with a delay of "120" seconds
