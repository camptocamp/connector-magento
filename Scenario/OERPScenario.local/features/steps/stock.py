# -*- coding: utf-8 -*-
from contextlib import closing, contextmanager
from support import *
import logging
from support.tools import model


@contextmanager
def newcr(ctx):
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']
    pool = openerp.modules.registry.RegistryManager.get(db_name)
    with closing(pool.db.cursor()) as cr:
        try:
            yield cr
        except:
            cr.rollback()
            raise
        else:
            cr.commit()

logger = logging.getLogger('openerp.behave')


@step('I recompute complete_name on stock.location')
def impl(ctx):
    Location = model('stock.location')
    locations = Location.search([])
    for location_id in locations:
        if location_id == 11:  # hang on Stock... let continue
            continue
        location = Location.get(location_id)
        location.write({'name': location.name})


@step('I recompute prices on 3-year old purchases')
def impl(ctx):
    with newcr(ctx) as cr:
        cr.execute("""
            UPDATE product_product
            SET last_purchase_price = new_years.price_unit
            FROM (
                SELECT years.product_id, years.price_unit FROM (
                    SELECT DISTINCT ON (product_id)
                    product_id, price_unit
                    FROM account_invoice_line
                    LEFT JOIN account_invoice
                    ON account_invoice_line.invoice_id = account_invoice.id
                    WHERE type = 'in_invoice'
                    AND state in ('open', 'paid')
                    AND price_unit > 0.0
                    AND quantity > 0.0
                    AND date_invoice >= CURRENT_DATE - INTERVAL '3 years'
                    ORDER BY product_id, date_invoice DESC,
                             account_invoice.id DESC) AS years, (
                    SELECT DISTINCT ON (product_id)
                    product_id, price_unit
                    FROM account_invoice_line
                    LEFT JOIN account_invoice
                    ON account_invoice_line.invoice_id = account_invoice.id
                    WHERE type = 'in_invoice'
                    AND state in ('open', 'paid')
                    AND price_unit > 0.0
                    AND quantity > 0.0
                    AND date_invoice >= CURRENT_DATE - INTERVAL '1 year'
                    ORDER BY product_id, date_invoice DESC,
                             account_invoice.id DESC) AS year
                WHERE years.product_id = year.product_id
                AND years.price_unit != year.price_unit) AS new_years
            WHERE id = new_years.product_id;

            SELECT years.product_id FROM (
                SELECT DISTINCT ON (product_id)
                product_id, price_unit
                FROM account_invoice_line
                LEFT JOIN account_invoice
                ON account_invoice_line.invoice_id = account_invoice.id
                WHERE type = 'in_invoice'
                AND state in ('open', 'paid')
                AND price_unit > 0.0
                AND quantity > 0.0
                AND date_invoice >= CURRENT_DATE - INTERVAL '3 years'
                ORDER BY product_id, date_invoice DESC,
                         account_invoice.id DESC) AS years, (
                SELECT DISTINCT ON (product_id)
                product_id, price_unit
                FROM account_invoice_line
                LEFT JOIN account_invoice
                ON account_invoice_line.invoice_id = account_invoice.id
                WHERE type = 'in_invoice'
                AND state in ('open', 'paid')
                AND price_unit > 0.0
                AND quantity > 0.0
                AND date_invoice >= CURRENT_DATE - INTERVAL '1 year'
                ORDER BY product_id, date_invoice DESC,
                         account_invoice.id DESC) AS year
            WHERE years.product_id = year.product_id
            AND years.price_unit != year.price_unit;
        """)
        rows = cr.fetchall()
    rows = dict((row[0], row[1]) for row in rows)

    Product = model('product.product')
    products = Product.browse(rows)
    for product in products:
        product.write({'name': product.name})
