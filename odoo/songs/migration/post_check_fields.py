# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import csv
import os

import anthem


@anthem.log
def update_base(ctx):
    """Update base

        To see which fields have been deleted in standard build,
        we need to do an update base which will recreate deleted fields.
    """
    ctx.env['ir.module.module'].search(
        [('name', '=', 'base')]
    ).button_immediate_upgrade()


@anthem.log
def check_fields(ctx):
    """Check fields

        Compare all fields defined in database between
        the fields before update of modules
        and the fields after update of modules.
        To avoid deletion of fields because
        a field has been moved from a module to another.
    """
    # Get the original fields saved in a CSV file before update of modules
    original_fields = {}
    # The explanation for the chosen directory is in the pre_check_fields.py
    with open('/data/odoo/pre_check_fields.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for model_name, module_name, field_name in reader:
            if model_name not in original_fields:
                original_fields[model_name] = {}
            if field_name not in original_fields[model_name]:
                original_fields[model_name][field_name] = []
            original_fields[model_name][field_name].append(module_name)

    # Get the final fields we have now in database
    final_fields = {}
    ctx.env.cr.execute(
        """
SELECT
    f.model AS model_name,
    d.module AS module_name,
    f.name AS field_name
FROM
    ir_model_fields f
INNER JOIN
    ir_model_data d
        ON f.id = d.res_id
        AND d.model = 'ir.model.fields'
        """
    )
    fields_data = ctx.env.cr.fetchall()
    for model_name, module_name, field_name in fields_data:
        if model_name not in final_fields:
            final_fields[model_name] = {}
        if field_name not in final_fields[model_name]:
            final_fields[model_name][field_name] = []
        final_fields[model_name][field_name].append(module_name)

    # For each fields we have now in database,
    # we will compare the list of modules
    # which define this field before and after the update of modules.
    for model_name, model_fields in final_fields.items():
        for field_name, field_modules in model_fields.items():
            if field_name in original_fields.get(model_name, {}):
                original_modules = set(original_fields[model_name][field_name])
                new_modules = set(field_modules)
                if original_modules and original_modules != new_modules:
                    # We have not the same list of modules:
                    # we display a line in build log.
                    ctx.log_line(
                        'PROBLEM ON DEFINED FIELD: '
                        'Model %s / '
                        'Field %s / '
                        'Old modules %s / '
                        'New modules %s'
                        % (
                            model_name,
                            field_name,
                            list(original_modules),
                            list(new_modules),
                        )
                    )


@anthem.log
def post(ctx):
    """POST: migration check fields"""
    env = os.environ.get('RUNNING_ENV')
    # We do the check only in dev mode.
    # To avoid to do the check each times,
    # the check is done only if it's not disabled in environment variables.
    if env == 'dev':
        migration_check_fields = os.environ.get('MIGRATION_CHECK_FIELDS')
        if migration_check_fields != 'True':
            ctx.log_line('If you never check the fields, please do it!')
        else:
            update_base(ctx)
            check_fields(ctx)
