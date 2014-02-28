# -*- coding: utf-8 -*-
from support import *


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


@given('I migrate the picking priorities modules')
def impl(ctx):
    with newcr(ctx) as cr:
        cr.execute("SELECT count(*) FROM stock_picking "
                   " WHERE priority = '3'")
        if not cr.fetchone()[0]:
            # already migrated
            return
        cr.execute("""
            UPDATE sale_order
            SET picking_priority = CASE packing_priority
                                WHEN '1' THEN '0'
                                WHEN '2' THEN '1'
                                WHEN '3' THEN '2'
                                ELSE packing_priority
                                END;
        """)
        cr.execute("""
            UPDATE stock_picking SET priority = CASE priority
                                WHEN '1' THEN '0'
                                WHEN '2' THEN '1'
                                WHEN '3' THEN '2'
                                ELSE priority
                                END;
        """)
