@debonix  @migration  @margin

Feature: install and configure the equivalence of products

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name             |
      | sale_markup      |
      | sale_floor_price |
    Then my modules should have been installed and models reloaded

  @markup_so
  Scenario: Clean markup computation on SO
    Given I execute the SQL commands
    # Compute missing cost_price based on price_unit, discount and commercial_margin
    """
    UPDATE sale_order_line SET cost_price = price_unit * ((100.0 - discount) / 100.0) - commercial_margin
        WHERE cost_price IS NULL AND commercial_margin IS NOT NULL AND price_unit IS NOT NULL;
    """
    Given I execute the SQL commands
    # Then try to complete cost_price with data from purchase_price set while using sale_margin module
    """
    UPDATE sale_order_line SET cost_price = purchase_price WHERE cost_price IS NULL AND purchase_price IS NOT NULL;
    """
    Given I execute the SQL commands
    # Recompute markup_rate in sale_order_line where result is wrong
    """
    UPDATE sale_order_line SET markup_rate = round((commercial_margin / (price_unit * ((100.0 - discount) / 100.0))) * 100, 2)
        WHERE price_unit <> 0 AND discount <> 100.0 AND abs(markup_rate - round((commercial_margin / (price_unit * ((100.0 - discount) / 100.0))) * 100, 2)) > 0.01;
    """

  @markup_product
  Scenario: Clean markup computation on product
    Given I execute the SQL commands
    """
    UPDATE product_product AS prod
      SET commercial_margin = list_price - cost_price
      FROM product_template AS tmpl
      WHERE tmpl.id = prod.product_tmpl_id
        AND abs(commercial_margin - (list_price - cost_price)) > 0.01;
    """
    Given I execute the SQL commands
    """
    UPDATE product_product AS prod
      SET markup_rate = (commercial_margin / list_price * 100.0)
      FROM product_template AS tmpl
      WHERE tmpl.id = prod.product_tmpl_id
        AND list_price <> 0
        AND abs(markup_rate - (commercial_margin / list_price * 100.0)) > 0.01;
    """
