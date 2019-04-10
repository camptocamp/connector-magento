# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall

UNINSTALL_MODULES_LIST = [
    # Here we need to list:
    # all modules installed in previous version of odoo,
    # but we don't want to keep.
]


@anthem.log
def update_state_for_uninstalled_modules(ctx):
    """ Update state for uninstalled modules
    to avoid to install/update them into the build """
    if UNINSTALL_MODULES_LIST:
        sql = """
            UPDATE
                ir_module_module
            SET
                state = 'uninstalled'
            WHERE
                name IN %s;
        """
        ctx.env.cr.execute(sql, [tuple(UNINSTALL_MODULES_LIST)])
    else:
        ctx.log_line("No modules to uninstall")


@anthem.log
def uninstall_modules(ctx):
    """ Uninstall modules """
    if UNINSTALL_MODULES_LIST:
        uninstall(ctx, UNINSTALL_MODULES_LIST)
    else:
        ctx.log_line("No modules to uninstall")


@anthem.log
def pre(ctx):
    """ PRE: uninstall """
    update_state_for_uninstalled_modules(ctx)


@anthem.log
def post(ctx):
    """ POST: uninstall """
    uninstall_modules(ctx)
