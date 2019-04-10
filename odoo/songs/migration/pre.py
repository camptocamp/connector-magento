# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os

import anthem
from openupgradelib.openupgrade import update_module_names
from psycopg2.extensions import AsIs

# from openupgradelib.openupgrade import update_module_moved_fields

# from .helper import update_module_moved_models

STORE_TYPES = {'ch': 's3', 'fr': 'swift'}
CUSTOMER_SHORTNAME = 'debonix'
PLATFORM = 'fr'


@anthem.log
def fix_path_on_attachments(ctx):
    """ Fix path on attachments """
    store_type = STORE_TYPES.get(PLATFORM)
    if not store_type:
        # Hosted on premise?
        ctx.log_line("No store_type: do nothing.")
        return
    env = os.environ.get('RUNNING_ENV')
    if env in ('prod', 'integration'):
        # Update attachment given by odoo for the database migration
        store_fname_root = ('{}://{}-odoo-{}/').format(
            store_type, CUSTOMER_SHORTNAME, env
        )
        query = """
            UPDATE
                ir_attachment
            SET
                store_fname = %s || store_fname
            WHERE
                store_fname IS NOT NULL
            AND store_fname NOT LIKE '%s://%%';
        """
        args = (store_fname_root, AsIs(store_type))
        ctx.env.cr.execute(query, args)
    else:
        # Remove the attachments
        query = """
            DELETE FROM
                ir_attachment
            WHERE
                store_fname IS NOT NULL
            AND store_fname LIKE '%s://%%';
        """
        args = (AsIs(store_type),)
        ctx.env.cr.execute(query, args)


@anthem.log
def rename_modules(ctx):
    """ Rename modules """
    update_module_names(
        ctx.env.cr,
        [
            # Here we need to list:
            # all modules on which
            # the module is renamed between the old and new version
            # Example:
            # ('account_financial_report_webkit', 'account_financial_report'),
        ],
        merge_modules=True,
    )


@anthem.log
def update_moved_models(ctx):
    """ Update model moved to another module """

    # When a model is moved to another module,
    # if the new module is updated before the old module is uninstalled,
    # the model is removed.

    # That function will update the metadata of the model
    # to indicate to Odoo the new module of the model.

    # Example:

    # update_module_moved_models(
    #     ctx.env.cr,
    #     [
    #         # Here we need to list:
    #         # all models which are moved in another module
    #
    #         'my.custom.model'
    #     ],
    #     'old_module',  # Old module of the models
    #     'new_module',  # New module of the models
    # )


@anthem.log
def update_moved_fields(ctx):
    """ Update fields moved to another module """

    # When a field is moved to another module,
    # if the new module is updated before the old module is uninstalled,
    # the field is removed.

    # That function will update the metadata of the field
    # to indicate to Odoo the new module of the field.

    # Example:

    # update_module_moved_fields(
    #     ctx.env.cr,
    #     'product.template',  # Model of the field
    #     ['purchase_ok'],  # Fields moved
    #     'invoice_webkit',  # Old module of the fields
    #     'product',  # New module of the fields
    # )


@anthem.log
def remove_all_custom_views(ctx):
    """ Remove all custom views """
    ctx.env['ir.ui.view.custom'].search([]).unlink()


@anthem.log
def remove_all_custom_filters(ctx):
    """ Remove all custom filters """
    ctx.env['ir.filters'].search([]).unlink()


@anthem.log
def remove_all_custom_exports(ctx):
    """ Remove all custom exports """

    # Before unlink all these exports,
    # you can install manually the module "base_export_manager"
    # which will add a menu: "Settings > Technical > Export Profiles".
    # With that, for a future usage,
    # you can get an export of all export you will delete.
    ctx.env['ir.exports'].search([]).unlink()


@anthem.log
def pre(ctx):
    """ PRE: migration """
    fix_path_on_attachments(ctx)
    rename_modules(ctx)
    update_moved_models(ctx)
    update_moved_fields(ctx)
    remove_all_custom_views(ctx)
    remove_all_custom_filters(ctx)
    remove_all_custom_exports(ctx)
