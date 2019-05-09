--
-- This file contains SQL requests to be run manually on copy of production database
-- in order to generate export CSV files based on the current data.
-- The generated files are then imported in Odoo using songs.
--
-- This file contains all requests we need to have to export payment terms.
--

--
-- Main request exporting payment terms (account.payment.term)
-- Saved to odoo/data/install/account_payment_term.csv
--
COPY
(
    SELECT
        '__setup__.account_payment_term_' || id AS id,
        name AS name,
        active::int AS active
    FROM
        account_payment_term
)
TO '/tmp/account_payment_term.csv'
DELIMITER ',' CSV HEADER;

--
-- Additional request for payment term lines (account.payment.term.line)
-- Saved to odoo/data/install/account_payment_term_line.csv
--
COPY
(
    SELECT
        '__setup__.account_payment_term_line_' || id AS id,
        '__setup__.account_payment_term_' || payment_id AS "payment_id/id",
        CASE
            WHEN value = 'procent'
                THEN 'percent'
            ELSE
                value
        END AS value,
        value_amount AS value_amount,
        days AS days,
        CASE
            WHEN days2 = -1
                THEN 31
            ELSE
                days2
        END AS day_of_the_month,
        sequence AS sequence
    FROM
        account_payment_term_line
    WHERE
        payment_id IS NOT NULL
    ORDER BY
        payment_id,
        value,
        id
)
TO '/tmp/account_payment_term_line.csv'
DELIMITER ',' CSV HEADER;
