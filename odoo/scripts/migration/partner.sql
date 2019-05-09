--
-- This file contains SQL requests to be run manually on copy of production database
-- in order to generate export CSV files based on the current data.
-- The generated files are then imported in Odoo using songs.
--
-- This file contains all requests we need to have to export partners.
--

--
-- Define partners to migrate
--

-- Add `to_migrate` column on res_partner
ALTER TABLE
    res_partner
ADD COLUMN
    to_migrate boolean;
-- Reset `to_migrate` values on res_partner
UPDATE
    res_partner
SET
    to_migrate = null;
-- Set partners to not migrate for partners with magento binding
UPDATE
    res_partner
SET
    to_migrate = False
WHERE
    id IN (
        SELECT openerp_id FROM magento_res_partner
    );
-- Set partners address to not migrate for partners with magento binding
UPDATE
    res_partner
SET
    to_migrate = False
WHERE
    parent_id IN (
        SELECT openerp_id FROM magento_res_partner
    );
-- Set partner "BERTON SICARD, GIL DEMIER" (749370) as not migrated (because many level of parents, and first linked to magento)
UPDATE
    res_partner
SET
    to_migrate = False
WHERE
    id = 749370;
-- Set partners to migrate for partners with current debit/credit
-- See: https://github.com/odoo/odoo/blob/7.0/addons/account/partner.py#L113
UPDATE
    res_partner
SET
    to_migrate = True
WHERE
    active = True
AND
    to_migrate is null
AND
    id IN (
        SELECT
            partner_id
        FROM
            account_move_line l
        LEFT JOIN
            account_account a ON (l.account_id = a.id)
        WHERE
            a.type IN ('receivable' , 'payable')
        AND
            l.reconcile_id IS NULL
        GROUP BY
            l.partner_id , a.type
        HAVING
            SUM(l.debit - l.credit) != 0
    );
-- Set partners to migrate for partners with tags
UPDATE
    res_partner
SET
    to_migrate = True
WHERE
    active = True
AND
    to_migrate is null
AND
    id IN (
        SELECT
            partner_id
        FROM
            res_partner_res_partner_category_rel
    );
-- Set partners to migrate for partners with recent sale orders in departments (74, 73, 01)
UPDATE
    res_partner
SET
    to_migrate = True
WHERE
    active = True
AND
    to_migrate is null
AND
    (zip LIKE '74%' OR zip LIKE '73%' OR zip LIKE '01%')
AND
    id IN (
        SELECT
            partner_id
        FROM
            sale_order
        WHERE
            state NOT IN ('draft' , 'sent', 'cancel')
        AND date_order >= '2018-01-01'
    );
-- Set partners to migrate for parents of all current partners to migrate
UPDATE
    res_partner
SET
    to_migrate = True
WHERE
    to_migrate is null
AND
    id IN (
        SELECT
            parent_id
        FROM
            res_partner
        WHERE
            to_migrate = True
    );


--
-- Main request exporting partners (res.partner)
-- Saved to odoo/data/install/res_partner.csv
--
COPY
(
    SELECT
        '__setup__.res_partner_' || p.id AS id,
        regexp_replace(p.name, E'[\\n\\r]+', ' ', 'g' ) AS name,
        p.is_company::int AS is_company,
        string_agg('__setup__.res_partner_category_' || category_rel.category_id, ',') AS "category_id/id",
        regexp_replace(p.street, E'[\\n\\r]+', ' ', 'g' ) AS street,
        regexp_replace(p.street2, E'[\\n\\r]+', ' ', 'g' ) AS street2,
        regexp_replace(p.city, E'[\\n\\r]+', ' ', 'g' ) AS city,
        CASE
            WHEN p.state_id = state_data.res_id
                THEN state_data.module || '.' || state_data.name
            WHEN p.state_id = 1
                THEN null
            ELSE
                'State problem: ' || p.state_id
        END AS "state_id/id",
        regexp_replace(p.zip, E'[\\n\\r]+', ' ', 'g' ) AS zip,
        CASE
            WHEN
                (
                    CASE
                        WHEN p.country_id = 263 THEN 41
                        WHEN p.country_id = 272 THEN 99
                        ELSE p.country_id
                    END = country_data.res_id
                )
                THEN country_data.module || '.' || country_data.name
            WHEN p.country_id IN (264, 265)
                THEN null
            ELSE
                'Country problem: ' || CASE WHEN p.country_id = 263 THEN 41 WHEN p.country_id = 272 THEN 99 ELSE p.country_id END
        END AS "country_id/id",
        regexp_replace(p.website, E'[\\n\\r]+', ' ', 'g' ) AS website,
        regexp_replace(p.phone, E'[\\n\\r]+', ' ', 'g' ) AS phone,
        regexp_replace(p.mobile, E'[\\n\\r]+', ' ', 'g' ) AS mobile,
        regexp_replace(p.email, E'[\\n\\r]+', ' ', 'g' ) AS email,
        '__setup__.res_partner_title_' || title AS "title/id",
        p.customer::int AS customer,
        p.supplier::int AS supplier,
        1 AS active,
        'stock.stock_location_customers' AS "property_stock_customer/id",
        'stock.stock_location_suppliers' AS "property_stock_supplier/id",
        '__setup__.account_payment_term_' || REPLACE(prop_term.value_reference, 'account.payment.term,', '') AS "property_payment_term_id/id",
        '__setup__.account_payment_term_' || REPLACE(prop_supplier_term.value_reference, 'account.payment.term,', '') AS "property_supplier_payment_term_id/id"
    FROM
        res_partner p
    LEFT JOIN
        res_partner_res_partner_category_rel category_rel
            ON p.id = category_rel.partner_id
    LEFT JOIN
        ir_model_data state_data
            ON state_data.model = 'res.country.state' AND p.state_id = state_data.res_id
    LEFT JOIN
        ir_model_data country_data
            ON country_data.model = 'res.country' AND CASE WHEN p.country_id = 263 THEN 41 WHEN p.country_id = 272 THEN 99 ELSE p.country_id END = country_data.res_id
    LEFT JOIN
        ir_property prop_term
            ON prop_term.name = 'property_payment_term' and prop_term.res_id = 'res.partner,' || p.id
    LEFT JOIN
        ir_property prop_supplier_term
            ON prop_supplier_term.name = 'property_supplier_payment_term' and prop_supplier_term.res_id = 'res.partner,' || p.id
    WHERE
        to_migrate = True
    GROUP BY
        p.id,
        state_data.id,
        country_data.id,
        prop_term.id,
        prop_supplier_term.id
)
TO '/tmp/res_partner.csv'
DELIMITER ',' CSV HEADER;

--
-- Additional request for partners multi-lines values (res.partner)
-- Saved to odoo/data/install/res_partner_descriptions.csv
--
COPY
(
    SELECT
        '__setup__.res_partner_' || id AS id,
        comment AS comment
    FROM
        res_partner
    WHERE
        to_migrate = True
    AND
        comment IS NOT NULL
)
TO '/tmp/res_partner_descriptions.csv'
DELIMITER ',' CSV HEADER;

--
-- Additional request for partners hierarchy (res.partner)
-- Saved to odoo/data/install/res_partner_parents.csv
--
COPY
(
    SELECT
        '__setup__.res_partner_' || p.id AS id,
        '__setup__.res_partner_' || p.parent_id AS "parent_id/id"
    FROM
        res_partner p
    INNER JOIN
        res_partner parent
            ON p.parent_id = parent.id
    WHERE
        p.to_migrate = True
)
TO '/tmp/res_partner_parents.csv'
DELIMITER ',' CSV HEADER;
