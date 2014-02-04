@debonix  @migration  @sale_exception

Feature: The sales orders must not be confirmed based on some conditions.
  As I write this scenario, the conditions to forbid the sale order confirmation are:
  - an ordered product is not in state "sellable"
  - the global markup rate of the sale order is too low
  - the customer is blocked
  - credit limit reached

  Besides this blocking conditions, a warning must be displayed when a customer reach its credit limit.
  I changed the credit limit warning to an exception, as it can be bypassed by a sale manager.
  If even a sale user must be able to confirm an order when the credit limit have been reached, we should
  implement a "warning" on sale_exception.

  So I do not need anymore the module c2c_block_customer_sale of version 5.

  Scenario: change the ir_model_data's entries to the new module's name
    Given I execute the SQL commands
    """
    UPDATE ir_model_data SET module = 'specific_sale_exceptions'
    WHERE module = 'specific_exceptions' and model = 'sale.exception';
    """

  Scenario: remove a carrier that make the install fails (removed from the module sale_exceptions)
    Given I find a "delivery.carrier" with oid: sale_exceptions.no_delivery_carrier
    Then I delete it

  Scenario: remove a product that make the install fails (removed from the module sale_exceptions)
    Given I find a "product.product" with oid: sale_exceptions.no_delivery_product
    Then I delete it

  Scenario: remove a partner that make the install fails (removed from the module sale_exceptions)
    Given I find a "res.partner" with oid: sale_exceptions.no_delivery_partner
    Then I delete it

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                     |
      | sale_exceptions          |
      | specific_sale_exceptions |
    Then my modules should have been installed and models reloaded
