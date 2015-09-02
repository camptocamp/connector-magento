# -*- coding: utf-8 -*-
@upgrade_from_1.1 @debonix

Feature: upgrade to 1.2.0

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | connector                        |
      | magentoerpconnect                |
      | server_env_magentoerpconnect     |
      | specific_magento                 |
      | elasticsearch_view_export        |
      | sql_view                         |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- Clean unsynched prices when a synced price exists
    DELETE FROM pricelist_partnerinfo
    WHERE (from_magento = False OR from_magento IS NULL)
    AND suppinfo_id IN (
        SELECT suppinfo_id
        FROM pricelist_partnerinfo
        WHERE from_magento = True
    );

    -- Called twice for one case with triplet
    DELETE FROM pricelist_partnerinfo
    WHERE id IN (
        SELECT min_id
        FROM (
            SELECT count(*) as cnt,
            min(id) as min_id
            FROM pricelist_partnerinfo
            GROUP BY suppinfo_id, min_quantity
        ) AS foo
        WHERE cnt > 1
    );

    DELETE FROM pricelist_partnerinfo
    WHERE id IN (
        SELECT min_id
        FROM (
            SELECT count(*) as cnt,
            min(id) as min_id
            FROM pricelist_partnerinfo
            GROUP BY suppinfo_id, min_quantity
        ) AS foo
        WHERE cnt > 1
    );

    -- Fix products with wrong magento ID
    UPDATE magento_product_product
    SET magento_id = 39695
    WHERE id = 28410;

    UPDATE magento_product_product
    SET magento_id = 19357
    WHERE id = 10590;
    """

    Given I create a SQL view "elk_purchase_order_report" named "Purchase Orders" with definition:
    """
     SELECT min(l.id) AS id,
        s.id as purchase_id,
        s.date_order AS date,
        to_char(s.date_order::timestamp with time zone, 'YYYY'::text) AS name,
        to_char(s.date_order::timestamp with time zone, 'MM'::text) AS month,
        to_char(s.date_order::timestamp with time zone, 'YYYY-MM-DD'::text) AS day,
        s.state,
        s.date_approve,
        s.minimum_planned_date AS expected_date,
        pricelist.name AS pricelist_name,
        validator_user.name AS validator_user_name,
        warehouse.name AS warehouse_name,
        supplier.name AS partner_name,
        create_user.name AS user_name,
        company.name AS company_name,
        product.default_code AS product_code,
        template.name AS product_name,
        categ.name AS product_category_name,
        template.uom_id AS product_uom_id,
        u2.name AS product_uom_name,
        location.name AS location_name,
        sum(l.product_qty / u.factor * u2.factor) AS quantity,
        date_part('epoch'::text, age(s.date_approve::timestamp with time zone, s.date_order::timestamp with time zone)) / (24 * 60 * 60)::numeric(16,2)::double precision AS delay,
        date_part('epoch'::text, age(l.date_planned::timestamp with time zone, s.date_order::timestamp with time zone)) / (24 * 60 * 60)::numeric(16,2)::double precision AS delay_pass,
        count(*) AS nbr,
        sum(l.price_unit * l.product_qty)::numeric(16,2) AS price_total,
        avg(100.0 * (l.price_unit * l.product_qty) / NULLIF(template.standard_price * l.product_qty / u.factor * u2.factor, 0.0))::numeric(16,2) AS negociation,
        sum(template.standard_price * l.product_qty / u.factor * u2.factor)::numeric(16,2) AS price_standard,
        (sum(l.product_qty * l.price_unit) / NULLIF(sum(l.product_qty / u.factor * u2.factor), 0.0))::numeric(16,2) AS price_average
       FROM purchase_order_line l
         JOIN purchase_order s ON s.id = l.order_id
         JOIN res_partner supplier ON supplier.id = s.partner_id
         JOIN res_company company ON company.id = s.company_id
         JOIN product_pricelist pricelist ON pricelist.id = s.pricelist_id
         LEFT JOIN stock_warehouse warehouse ON warehouse.id = s.warehouse_id
         LEFT JOIN stock_location location ON location.id = s.location_id
         LEFT JOIN product_product product ON product.id = l.product_id
         LEFT JOIN product_template template ON template.id = product.product_tmpl_id
         LEFT JOIN product_category categ ON categ.id = template.categ_id
         LEFT JOIN product_uom u ON u.id = l.product_uom
         LEFT JOIN product_uom u2 ON u2.id = template.uom_id
         LEFT JOIN res_users validator_user ON validator_user.id = s.validator
         LEFT JOIN res_users create_user ON create_user.id = s.create_uid
      GROUP BY s.id,
               company.name,
               create_user.name,
               supplier.name,
               u.factor,
               location.name,
               l.price_unit,
               s.date_approve,
               l.date_planned,
               l.product_uom,
               s.minimum_planned_date,
               pricelist.name,
               validator_user.name,
               product.default_code,
               template.name,
               categ.name,
               s.date_order,
               to_char(s.date_order::timestamp with time zone, 'YYYY'::text),
               to_char(s.date_order::timestamp with time zone, 'MM'::text),
               to_char(s.date_order::timestamp with time zone, 'YYYY-MM-DD'::text),
               s.state,
               warehouse.name,
               u.uom_type,
               u.category_id,
               template.uom_id,
               u.id,
               u2.name,
               u2.factor
    """

    Given I create a SQL view "elk_sale_order_report" named "Sales Orders" with definition:
    """
     SELECT
       sale_order_line.id AS so_line_id,
       sale_order_line.name AS so_line_name,
       sale_order_line.price_unit AS so_line_price_unit,
       sale_order_line.product_uom_qty AS so_line_product_uom_qty,
       (sale_order_line.product_uom_qty * sale_order_line.price_unit) AS so_line_product_subtotal,
       sale_order_line.product_uom AS product_uom_id,
       uom.name AS product_uom_name,
       sale_order_line.product_uos_qty AS quantity,
       sale_order_line.product_uos AS product_uos_id,
       uos.name AS product_uos_name,
       sale_order_line.product_id AS product_id,
       product_product.default_code AS product_code,
       product_template.name AS product_name,
       sale_order_line.state AS so_line_state,
       sale_order_line.invoiced AS so_line_invoiced,
       sale_order_line.discount AS so_line_discount,
       sale_order_line.commercial_margin AS so_line_commercial_margin,
       sale_order_line.markup_rate AS so_line_markup_rate,
       sale_order_line.cost_price AS so_line_cost_price,
       sale_order.id AS so_id,
       sale_order.name AS so_name,
       product_pricelist.id AS pricelist_id,
       product_pricelist.name AS pricelist_name,
       res_currency.name AS currency,
       sale_order.state AS so_state,
       sale_order.origin AS so_origin,
       sale_order.date_order AS so_date_order,
       sale_order.date_confirm AS so_date_confirm,
       res_partner.id AS partner_id,
       res_partner.name AS partner_name,
       res_country.name as partner_country,
       sale_order.user_id AS user_id,
       res_users.name AS user_name,
       sale_shop.name AS shop_name,
       sale_order.project_id AS aa_id,
       account_analytic_account.code AS aa_code,
       account_analytic_account.name AS aa_name
     FROM sale_order
       JOIN sale_order_line on (sale_order.id = sale_order_line.order_id)
       LEFT JOIN product_product on (product_product.id = sale_order_line.product_id)
       JOIN product_template on (product_template.id = product_product.product_tmpl_id)
       JOIN product_pricelist on (product_pricelist.id = sale_order.pricelist_id)
       JOIN res_currency on (res_currency.id = product_pricelist.currency_id)
       JOIN res_partner on (res_partner.id = sale_order.partner_id)
       JOIN sale_shop on (sale_shop.id = sale_order.shop_id)
       LEFT JOIN res_country on (res_country.id = res_partner.country_id)
       LEFT JOIN account_analytic_account on (account_analytic_account.id = sale_order.project_id)
       LEFT JOIN res_users on (res_users.id = sale_order.user_id)
       LEFT JOIN product_uom uom on (uom.id = sale_order_line.product_uom)
       LEFT JOIN product_uom uos on (uos.id = sale_order_line.product_uos)
    """

    Given I create a SQL view "elk_stock_move_in_out" named "Stock Moves (in/out)" with definition:
    """
    (
    SELECT
          min(m.id) as id,
          m.date as date,
          to_char(m.date, 'YYYY') as year,
          to_char(m.date, 'MM') as month,
          m.partner_id as partner_id,
          m.location_id as location_id,
          m.product_id as product_id,
          pt.categ_id as product_categ_id,
          l.usage as location_type,
          l.scrap_location as scrap_location,
          m.company_id,
          m.state as state,
          m.prodlot_id as prodlot_id,

          coalesce(sum(-pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
          coalesce(sum(-m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty,
          0.0 AS product_qty_in,
          coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) AS product_qty_out
      FROM
          stock_move m
              LEFT JOIN stock_picking p ON (m.picking_id=p.id)
              LEFT JOIN product_product pp ON (m.product_id=pp.id)
                  LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                  LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                  LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
              LEFT JOIN product_uom u ON (m.product_uom=u.id)
              LEFT JOIN stock_location l ON (m.location_id=l.id)
              WHERE m.state != 'cancel'
      GROUP BY
          m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id,  m.location_dest_id,
          m.prodlot_id, m.date, m.state, l.usage, l.scrap_location, m.company_id, pt.uom_id, to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
    ) UNION ALL (
      SELECT
          -m.id as id, m.date as date,
          to_char(m.date, 'YYYY') as year,
          to_char(m.date, 'MM') as month,
          m.partner_id as partner_id,
          m.location_dest_id as location_id,
          m.product_id as product_id,
          pt.categ_id as product_categ_id,
          l.usage as location_type,
          l.scrap_location as scrap_location,
          m.company_id,
          m.state as state,
          m.prodlot_id as prodlot_id,
          coalesce(sum(pt.standard_price * m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
          coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty,
          coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty_in,
          0.0 as product_qty_out
      FROM
          stock_move m
              LEFT JOIN stock_picking p ON (m.picking_id=p.id)
              LEFT JOIN product_product pp ON (m.product_id=pp.id)
                  LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                  LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                  LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
              LEFT JOIN product_uom u ON (m.product_uom=u.id)
              LEFT JOIN stock_location l ON (m.location_dest_id=l.id)
              WHERE m.state != 'cancel'
      GROUP BY
          m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id, m.location_dest_id,
          m.prodlot_id, m.date, m.state, l.usage, l.scrap_location, m.company_id, pt.uom_id, to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
    )
    """

    Given I create a SQL view "elk_stock_move_cumulative" named "Stock Moves (Cumulative)" with definition:
    """
    SELECT
      DATE_TRUNC('MONTH', date) AS month,
      location_id,
      product_id,
      company_id,
      product_categ_id,
      state,
      SUM(product_qty_in) AS qty_in,
      SUM(product_qty_out) AS qty_out,
      SUM(product_qty_in) - SUM(product_qty_out) AS qty_diff,
      (SUM(SUM(product_qty_in)) OVER w - SUM(SUM(product_qty_out)) OVER w) - SUM(product_qty_in) + SUM(product_qty_out) AS qty_cumul_start,
      SUM(SUM(product_qty_in)) OVER w - SUM(SUM(product_qty_out)) OVER w AS qty_cumul_end,
      SUM(value) AS value,
      (SUM(SUM(value)) OVER w) - SUM(value) AS value_cumul_start,
      SUM(SUM(value)) OVER w AS value_cumul_end
    FROM view_elk_stock_move_in_out
    GROUP BY
      DATE_TRUNC('MONTH', date),
      location_id,
      product_id,
      company_id,
      product_categ_id,
      state
    WINDOW w AS (
      PARTITION BY
        location_id,
        product_id,
        company_id,
        product_categ_id,
        state
      ORDER BY DATE_TRUNC('MONTH', date)
    )
    ORDER BY DATE_TRUNC('MONTH', date)
    """

    Given I create a SQL view "elk_stock_move_turnover" named "Stock Moves (Turnover)" with definition:
    """
    SELECT
      m.month,
      m.location_id,
      location.name AS location_name,
      m.product_id,
      product.default_code AS product_code,
      product_template.name AS product_name,
      m.company_id,
      company.name AS company_name,
      m.product_categ_id,
      product_category.name AS product_category_name,
      m.qty_in,
      m.qty_out,
      m.qty_diff,
      m.qty_cumul_start,
      m.qty_cumul_end,
      CASE m.qty_cumul_start + m.qty_cumul_end
        WHEN 0 THEN 0.0
        ELSE m.qty_out / ((m.qty_cumul_start + m.qty_cumul_end) / 2)
      END AS qty_turnover,
      m.value,
      m.value_cumul_start,
      m.value_cumul_end
    FROM view_elk_stock_move_cumulative m
    JOIN stock_location location
    ON location.id = m.location_id
    JOIN product_product product
    ON product.id = m.product_id
    JOIN product_template
    ON product_template.id = product.product_tmpl_id
    JOIN product_category
    ON product_category.id = m.product_categ_id
    JOIN res_company company
    ON company.id = m.company_id
    WHERE
      m.state = 'done'
    ORDER BY month
    """

    Given I set the version of the instance to "1.2.0"
