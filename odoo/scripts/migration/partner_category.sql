--
-- This file contains SQL requests to be run manually on copy of production database
-- in order to generate export CSV files based on the current data.
-- The generated files are then imported in Odoo using songs.
--
-- This file contains all requests we need to have to export partner categories.
--

--
-- Main request exporting partner categories (res.partner.category)
-- Saved to odoo/data/install/res_partner_category.csv
--
COPY
(
    SELECT
        '__setup__.res_partner_category_' || id AS id,
        name AS name,
        active::int AS active
    FROM
        res_partner_category
)
TO '/tmp/res_partner_category.csv'
DELIMITER ',' CSV HEADER;

--
-- Additional request for partner categories hierarchy (res.partner.category)
-- Saved to odoo/data/install/res_partner_category_parents.csv
--
COPY
(
    SELECT
        '__setup__.res_partner_category_' || id AS id,
        '__setup__.res_partner_category_' || parent_id AS "parent_id/id"
    FROM
        res_partner_category
    WHERE
        parent_id IS NOT NULL
)
TO '/tmp/res_partner_category_parents.csv'
DELIMITER ',' CSV HEADER;
