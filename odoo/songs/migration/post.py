# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from odoo.exceptions import UserError
from odoo.modules.module import load_information_from_description_file


@anthem.log
def database_cleanup(ctx):
    """ Clean database """

    # Clean models from uninstalled modules
    ctx.log_line('Start purging models')
    try:
        purge_models = ctx.env['cleanup.purge.wizard.model'].create({})
        purge_model_lines = purge_models.purge_line_ids
        for purge_model_line in purge_model_lines:
            ctx.log_line('Try to purge: %s' % purge_model_line.name)
            purge_model_line.purge()
    except UserError as e:
        ctx.log_line("Cleanup resulted in error: '{}'".format(str(e)))

    # Clean columns/fields from uninstalled modules
    ctx.log_line('Start purging columns')
    try:
        purge_columns = ctx.env['cleanup.purge.wizard.column'].create({})
        purge_column_lines = purge_columns.purge_line_ids.filtered(
            lambda l: l.name
            not in [
                # Due to a bug on database_cleanup module in v12,
                # the column password of res.users is removed.
                # See comments: https://github.com/OCA/server-tools/pull/1408
                # So we just ignore that column here.
                'password'
            ]
        )
        for purge_column_line in purge_column_lines:
            ctx.log_line('Try to purge: %s' % purge_column_line.name)
            purge_column_line.purge()
    except UserError as e:
        ctx.log_line("Cleanup resulted in error: '{}'".format(str(e)))

    # Clean tables from uninstalled modules
    ctx.log_line('Start purging tables')
    try:
        purge_tables = ctx.env['cleanup.purge.wizard.table'].create({})
        purge_table_lines = purge_tables.purge_line_ids.filtered(
            lambda l: l.name
            not in [
                # The marabunta_version table must never be deleted
                'marabunta_version'
            ]
        )
        for purge_table_line in purge_table_lines:
            ctx.log_line('Try to purge: %s' % purge_table_line.name)
            purge_table_line.purge()
    except UserError as e:
        ctx.log_line("Cleanup resulted in error: '{}'".format(str(e)))

    # Clean models data from uninstalled modules
    ctx.log_line('Start purging datas')
    try:
        purge_datas = ctx.env['cleanup.purge.wizard.data'].create({})
        purge_data_lines = purge_datas.purge_line_ids.filtered(
            # Metadata exported, imported or from setup must not be deleted
            lambda l: '__export__' not in l.name
            and '__setup__' not in l.name
            and '__import__' not in l.name
        )
        for purge_data_line in purge_data_lines:
            ctx.log_line('Try to purge: %s' % purge_data_line.name)
            purge_data_line.purge()
    except UserError as e:
        ctx.log_line("Cleanup resulted in error: '{}'".format(str(e)))

    # Clean menus from uninstalled modules
    ctx.log_line('Start purging menus')
    try:
        purge_menus = ctx.env['cleanup.purge.wizard.menu'].create({})
        purge_menu_lines = purge_menus.purge_line_ids
        for purge_menu_line in purge_menu_lines:
            ctx.log_line('Try to purge: %s' % purge_menu_line.name)
            purge_menu_line.purge()
    except UserError as e:
        ctx.log_line("Cleanup resulted in error: '{}'".format(str(e)))


@anthem.log
def clean_unavailable_modules(ctx):
    """Clean unavailable modules

        When we migrate a project,
        we have a lot of modules which became unavailable in the new version.
        This function will clean the module list to delete unavailable modules.
    """
    module_model = ctx.env['ir.module.module']
    all_modules = module_model.search(
        [
            # Here we need to list:
            # all modules uninstalled we want to migrate
            # to avoid to remove them
            # Example:
            # (
            #     'name',
            #     'not in',
            #     [
            #         'account_asset_management',              # To migrate!
            #     ]
            # )
        ]
    )
    for module in all_modules:
        info = load_information_from_description_file(module.name)
        if not info:
            if module.state in ['uninstalled', 'uninstallable']:
                ctx.log_line(
                    'MODULE UNAVAILABLE (will be deleted) : %s' % module.name
                )
                if ctx.env['ir.model.data'].search(
                    [('module', '=', module.name)]
                ):
                    ctx.log_line(
                        "===> CAN'T UNLINK MODULE, WE HAVE METADATA "
                        "(See if we want to migrate or uninstall the module)"
                    )
                else:
                    module.unlink()
            else:
                ctx.log_line(
                    'MODULE UNAVAILABLE BUT BAD STATE : %s (%s)'
                    % (module.name, module.state)
                )

    module_model.update_list()


@anthem.log
def post(ctx):
    """ POST: migration """
    # Check the list of cleaned data before uncomment the call of this function
    # database_cleanup(ctx)
    clean_unavailable_modules(ctx)
