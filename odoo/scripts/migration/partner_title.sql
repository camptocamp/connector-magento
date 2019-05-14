--
-- This file contains SQL requests to be run manually on copy of production database
-- in order to generate export CSV files based on the current data.
-- The generated files are then imported in Odoo using songs.
--
-- This file contains all requests we need to have to export partner titles.
--

--
-- Main request exporting partner titles (res.partner.title)
-- Saved to odoo/data/install/res_partner_title.csv
--
COPY
(
    SELECT
        '__setup__.res_partner_title_' || id AS id,
        name AS name,
        shortcut AS shortcut
    FROM
        res_partner_title
)
TO '/tmp/res_partner_title.csv'
DELIMITER ',' CSV HEADER;
