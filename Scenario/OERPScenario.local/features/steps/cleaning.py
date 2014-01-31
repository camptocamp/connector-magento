# -*- coding: utf-8 -*-
from contextlib import closing, contextmanager
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')


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
        else:
            cr.commit()


@step('I delete all the {model_name} records created by uninstalled modules')
def impl(ctx, model_name):
    """
    Delete the records from `model_name` referenced by an entry in
    `ir.model.data` that is from an uninstalled module.

    Example of models that could be cleaned:
        ir.ui.view
        ir.ui.menu
        ir.act_window
        ir.actions.act_window.view
        ir.act.report.xml
        ir.actions.todo
        ir.act.wizard
        ir.cron
        ir.model.access
        ir.module.repository
        ir.report.custom
        ir.report.custom.fields
        ir.ui.view_sc
        ir.values
        ir.rule
        ir.rule.group
        res.group

    """
    modules = model('ir.module.module').browse(['state = installed'])
    module_names = [m.name for m in modules]
    entries = model('ir.model.data').browse([('module', 'not in', module_names),
                                             ('model', '=', model_name)])

    with newcr(ctx) as cr:
        table = model_name.replace('.', '_')
        table_delete_ids = set()
        entry_delete_ids = set()
        for entry in entries:
            cr.execute("SELECT * FROM information_schema.tables "
                       "WHERE table_name = %s", (table,))
            if cr.fetchone()[0]:  # the table exists
                table_delete_ids.add(entry.res_id)
            entry_delete_ids.add(entry.id)
        cr.execute("DELETE FROM %s WHERE id IN %%s" % table,
                   (tuple(table_delete_ids),))
        cr.execute("DELETE FROM ir_model_data WHERE id IN %s",
                   (tuple(entry_delete_ids),))
