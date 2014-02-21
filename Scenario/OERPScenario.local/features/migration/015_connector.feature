@debonix  @migration  @connector

Feature: install and configure the modules related to the magento connector

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                         |
      | magentoerpconnect            |
      | specific_magento             |
      | server_env_magentoerpconnect |
    Then my modules should have been installed and models reloaded

  @backend
  Scenario: Configure the magento backend
    Given I need a "magento.backend" with oid: scenario.magento_backend_debonix
    And having:
         | key                 | value                                                                            |
         | name                | debonix                                                                          |
         | version             | 1.7-debonix                                                                      |
         | warehouse_id        | by oid: stock.warehouse0                                                         |
         | default_lang_id     | by code: fr_FR                                                                   |
    And I press the button "synchronize_metadata"

  Scenario: migrate the products categories external ids
    Given I execute the SQL commands
    """
    INSERT INTO magento_product_category (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date, description) 
    SELECT res_id,
           replace(name, 'product_category/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           (SELECT last_products_export_date FROM sale_shop WHERE id = 2),
           1,
           1,
           create_date,
           write_date,
           (SELECT description FROM product_category WHERE id = id.res_id)
           FROM ir_model_data id
    WHERE model = 'product.category'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_product_category c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'product_category/', '') = c.magento_id);
    """

  Scenario: migrate the products external ids
    Given I execute the SQL commands
    """
    INSERT INTO magento_product_product (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date, product_type, manage_stock, backorders) 
    SELECT res_id,
           replace(name, 'product_product/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           (SELECT last_products_export_date FROM sale_shop WHERE id = 2),
           1,
           1,
           create_date,
           write_date,
           (SELECT product_type FROM product_product WHERE id = id.res_id),
           (SELECT CASE magento_manage_stock WHEN true THEN 'use_default' ELSE 'no' END FROM product_product WHERE id = id.res_id),
           (SELECT CASE magento_backorders WHEN '0' THEN 'use_default' WHEN '1' THEN 'yes' WHEN '2' THEN 'no' END FROM product_product WHERE id = id.res_id)
           FROM ir_model_data id
    WHERE model = 'product.product'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_product_product c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'product_product/', '') = c.magento_id);
    """
    # TODO: set the magento_qty to the current stock level
