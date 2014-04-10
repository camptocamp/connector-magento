@debonix  @migration  @connector

Feature: install and configure the modules related to the magento connector

  @magento_fidelity
  Scenario: the fidelity product is now in specific_magento instead of magento_fidelity
    Given I execute the SQL commands
    """
    UPDATE ir_model_data SET module = 'specific_magento'
    WHERE module = 'magento_fidelity' AND name = 'product_product_debonix_fidelity';
    """

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name                         |
      | magentoerpconnect            |
      | magentoerpconnect_pricing    |
      | product_brand                |
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

  Scenario: set import dates
    Given I execute the SQL commands
    """
    UPDATE magento_backend
    SET import_categories_from_date = (SELECT last_products_export_date FROM sale_shop WHERE id = 2),
        import_products_from_date = (SELECT last_products_export_date FROM sale_shop WHERE id = 2);

    UPDATE magento_website
    SET import_partners_from_date = now();

    UPDATE magento_storeview
    SET import_orders_from_date = (SELECT max(date_order) FROM sale_order);
    """

  Scenario: migrate the sale_shop
    Given I execute the SQL commands
    """
    UPDATE magento_store SET openerp_id = 2 WHERE openerp_id IN (SELECT id FROM sale_shop WHERE name = 'Debonix Store Group');
    DELETE FROM sale_shop WHERE name = 'Debonix Store Group' AND id NOT IN (SELECT openerp_id FROM magento_store);
    """

  Scenario: migrate the products categories external ids
    Given I execute the SQL commands
    """
    INSERT INTO magento_product_category (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                          description)
    SELECT res_id,
           replace(id.name, 'product_category/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           (SELECT to_char(last_products_export_date, 'YYYY-MM-DD HH24:MI:SS')::timestamp FROM sale_shop WHERE id = 2),
           1,
           1,
           id.create_date,
           id.write_date,
           -- \n
           pc.description
    FROM ir_model_data id
    INNER JOIN product_category pc ON pc.id = id.res_id
    WHERE model = 'product.category'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_product_category c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'product_category/', '') = c.magento_id);
    """

  Scenario: migrate the products external ids
    Given I execute the SQL commands
    """
    INSERT INTO magento_product_product (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                         product_type, manage_stock, backorders, updated_at, created_at)
    SELECT res_id,
           replace(id.name, 'product_product/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           (SELECT to_char(last_products_export_date, 'YYYY-MM-DD HH24:MI:SS')::timestamp FROM sale_shop WHERE id = 2),
           1,
           1,
           id.create_date,
           id.write_date,
           -- \n
           pp.product_type,
           CASE pp.magento_manage_stock WHEN true THEN 'use_default' ELSE 'no' END,
           CASE pp.magento_backorders WHEN '0' THEN 'use_default' WHEN '1' THEN 'yes' WHEN '2' THEN 'no' END,
           pp.updated_at,
           pp.created_at
    FROM ir_model_data id
    INNER JOIN product_product pp ON pp.id = id.res_id
    WHERE model = 'product.product'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_product_product c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'product_product/', '') = c.magento_id);
    """
    # TODO: set the magento_qty to the current stock level

  Scenario: migrate the customer groups
    Given I execute the SQL commands
    """
    INSERT INTO magento_res_partner_category (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                              tax_class_id)
    SELECT res_id,
           replace(id.name, 'res_partner_category/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           to_char(now(), 'YYYY-MM-DD HH24:MI:SS')::timestamp,
           1,
           1,
           id.create_date,
           id.write_date,
           -- \n
           pc.tax_class_id
    FROM ir_model_data id
    INNER JOIN res_partner_category pc ON pc.id = id.res_id
    WHERE model = 'res.partner.category'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_res_partner_category c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'res_partner_category/', '') = c.magento_id);
    """

  Scenario: migrate the partners
    Given I execute the SQL commands
    """
    INSERT INTO magento_res_partner (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                     emailid, taxvat, newsletter, consider_as_company, website_id, guest_customer, group_id, updated_at, created_at) 
    SELECT res_id,
           replace(id.name, 'res_partner/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           to_char(now(), 'YYYY-MM-DD HH24:MI:SS')::timestamp,
           1,
           1,
           id.create_date,
           id.write_date,
           -- \n
           rp.emailid,
           rp.mag_vat,
           rp.mag_newsletter,
           false, -- we can't know if it has a company name
           (SELECT id FROM magento_website where code = 'debonix_website'),
           false,
           mc.id,
           rp.updated_at,
           rp.created_at
    FROM ir_model_data id
    INNER JOIN res_partner rp ON rp.id = id.res_id
    LEFT OUTER JOIN res_partner_category pc ON pc.id = rp.group_id
    LEFT OUTER JOIN magento_res_partner_category mc ON mc.openerp_id = pc.id
    WHERE model = 'res.partner'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_res_partner c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'res_partner/', '') = c.magento_id);

    """

  Scenario: migrate the addresses
    Given I execute the SQL commands
    """
      INSERT INTO magento_address (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                 magento_partner_id, is_magento_order_address, is_default_shipping, is_default_billing, website_id, updated_at, created_at) 
    SELECT pa.partner_id,
           replace(id.name, 'res_partner_address/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           to_char(now(), 'YYYY-MM-DD HH24:MI:SS')::timestamp,
           1,
           1,
           id.create_date,
           id.write_date,
           -- \n
           mp.id,
           pa.is_magento_order_address,
           CASE pa.type WHEN 'default' THEN true WHEN 'delivery' THEN true ELSE false END,
           CASE pa.type WHEN 'default' THEN true WHEN 'invoice' THEN true ELSE false END,
           (SELECT id FROM magento_website where code = 'debonix_website'),
           rp.updated_at,
           rp.created_at
    FROM ir_model_data id
    INNER JOIN res_partner_address pa ON pa.id = id.res_id
    INNER JOIN res_partner rp ON rp.id = pa.old_partner_id  -- parent_id
    INNER JOIN magento_res_partner mp ON rp.id = mp.openerp_id
    WHERE model = 'res.partner.address'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_address c
                    WHERE pa.partner_id = c.openerp_id AND replace(id.name, 'res_partner_address/', '') = c.magento_id)
    """

  @sale_order
  Scenario: migrate the sales orders
    Given I execute the SQL commands
    """
    INSERT INTO magento_sale_order (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                    total_amount, total_amount_tax, magento_parent_id, magento_order_id) 
    SELECT id.res_id,
           replace(id.name, 'sale_order/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           to_char(now(), 'YYYY-MM-DD HH24:MI:SS')::timestamp,
           1,
           1,
           id.create_date,
           id.write_date,
           -- \n
           so.amount_total,
           so.amount_tax,
           -- we do not have theses informations
           null,
           null
    FROM ir_model_data id
    INNER JOIN sale_order so
    ON so.id = id.res_id
    WHERE model = 'sale.order'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_sale_order c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'sale_order/', '') = c.magento_id);
    """

  Scenario: migrate the pickings
    Given I execute the SQL commands
    """
    INSERT INTO magento_stock_picking_out (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                              magento_order_id, picking_method) 
    SELECT res_id,
           replace(id.name, 'stock_picking/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           to_char(now(), 'YYYY-MM-DD HH24:MI:SS')::timestamp,
           1,
           1,
           id.create_date,
           id.write_date,
           -- \n
           ms.id,
           'complete'
    FROM ir_model_data id
    INNER JOIN stock_picking sp ON sp.id = id.res_id
    INNER JOIN magento_sale_order ms ON ms.openerp_id = sp.sale_id
    WHERE model = 'stock.picking'
    AND external_referential_id = 1
    AND NOT EXISTS (SELECT id FROM magento_stock_picking_out c
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'stock_picking/', '') = c.magento_id);
    """

  Scenario: migrate the brands from magento attributes to product_brand
    Given I execute the SQL commands
    """
    INSERT INTO product_brand (create_uid, write_uid, create_date, write_date, name)
    SELECT create_uid, write_uid, create_date, write_date, label FROM magerp_product_attribute_options
    WHERE attribute_id = 193
    AND NOT EXISTS (SELECT id FROM product_brand WHERE name = label);

    INSERT INTO magento_product_brand (create_uid, write_uid, create_date, write_date, openerp_id, magento_id, sync_date, backend_id)
    SELECT b.create_uid, b.write_uid, b.create_date, b.write_date, b.id, o.value,
           to_char(now(), 'YYYY-MM-DD HH24:MI:SS')::timestamp,
           (SELECT id FROM magento_backend LIMIT 1)
    FROM product_brand b
    INNER JOIN magerp_product_attribute_options o
    ON o.label = b.name
    WHERE o.attribute_id = 193
    AND NOT EXISTS (SELECT id FROM magento_product_brand WHERE openerp_id = b.id);

    UPDATE product_template AS t SET product_brand_id = b.id
    FROM product_brand b, product_product p, magerp_product_attribute_options  o
    WHERE o.label = b.name
    AND p.product_tmpl_id = t.id
    AND o.id = p.x_magerp_marque
    AND o.attribute_id = 193;

    """

  @workflow
  Scenario: Configure the workflows
    Given I find a "sale.workflow.process" with oid: sale_automatic_workflow.manual_validation
    And having:
      | key               | value           |
      | create_invoice_on | on_picking_done |
      | validate_invoice  | True            |

  @payment_method
  Scenario: Migrate the payment methods
    Given I migrate the payment methods
    And I set the new payment methods on the sales orders

  @special_products
  Scenario Outline: Configure the special products otherwise they cannot be sold
    Given I find a "product.product" with oid: <oid>
    And having:
      | key               | value           |
      | state             | sellable        |

  Examples:
      | oid                                                  |
      | connector_ecommerce.product_product_shipping         |
      | connector_ecommerce.product_product_cash_on_delivery |
      | connector_ecommerce.product_product_gift             |
      | connector_ecommerce.product_product_discount         |

  @carrier
  Scenario: the magento_code is now the full name (it was chronopost and should be chronopost_Chrono10, the name actually)
    Given I execute the SQL commands
    """
    UPDATE delivery_carrier SET magento_code = name
    WHERE magento_code not like '%\_%' and magento_code is not null;
    """

  @fidelity_product
  Scenario: the fidelity product has to be a taxes included product
    Given I find a "product.product" with oid: specific_magento.product_product_debonix_fidelity
    And having:
      | key      | value     |
      | taxes_id | by id: 43 |
