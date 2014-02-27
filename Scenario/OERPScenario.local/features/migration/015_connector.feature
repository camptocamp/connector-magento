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
    INSERT INTO magento_product_category (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                          description)
    SELECT res_id,
           replace(id.name, 'product_category/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           (SELECT last_products_export_date FROM sale_shop WHERE id = 2),
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
           (SELECT last_products_export_date FROM sale_shop WHERE id = 2),
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
           now(),
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
           now(),
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
           now(),
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
                    WHERE id.res_id = c.openerp_id AND replace(id.name, 'res_partner_address/', '') = c.magento_id)
    """

  Scenario: migrate the sales orders
    Given I execute the SQL commands
    """
    INSERT INTO magento_sale_order (openerp_id, magento_id, backend_id, sync_date, create_uid, write_uid, create_date, write_date,
                                    total_amount, total_amount_tax, magento_parent_id, magento_order_id) 
    SELECT res_id,
           replace(name, 'sale_order/', ''),
           (SELECT id FROM magento_backend LIMIT 1),
           now(),
           1,
           1,
           create_date,
           write_date,
           -- \n
           -- we do not have theses informations
           null,
           null,
           null,
           null
    FROM ir_model_data id
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
           now(),
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
