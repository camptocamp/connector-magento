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
            raise
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
        ir.actions.act_window
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
        if model_name == 'ir.actions.act_window':
            table = 'ir_act_window'
        elif model_name == 'ir.actions.wizard':
            table = 'ir_act_wizard'
        else:
            table = model_name.replace('.', '_')
        table_delete_ids = set()
        entry_delete_ids = set()
        for entry in entries:
            cr.execute("SELECT * FROM information_schema.tables "
                       "WHERE table_name = %s", (table,))
            if cr.fetchone():  # the table exists
                table_delete_ids.add(entry.res_id)
            entry_delete_ids.add(entry.id)
        ir_values = ['%s,%d' % (model_name, tid) for tid in table_delete_ids]
        if ir_values:
            cr.execute("DELETE FROM ir_values WHERE value in %s",
                       (tuple(ir_values),))
        if table_delete_ids:
            cr.execute("DELETE FROM %s WHERE id IN %%s" % table,
                       (tuple(table_delete_ids),))
        if entry_delete_ids:
            cr.execute("DELETE FROM ir_model_data WHERE id IN %s",
                       (tuple(entry_delete_ids),))


@step('I delete the broken ir.values')
def impl(ctx):
    """ Remove ir.values referring to not existing actions """
    with newcr(ctx) as cr:
        # we'll maybe need to remove other types than
        # ir.actions.act_window
        cr.execute(
            "DELETE "
            "FROM ir_values v "
            "WHERE NOT EXISTS ( "
            " SELECT id FROM ir_act_window "
            " WHERE id = replace(v.value, 'ir.actions.act_window,', '')::int) "
            "AND key = 'action' "
            "AND value LIKE 'ir.actions.act_window,%' "
        )
