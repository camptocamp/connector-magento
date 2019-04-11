# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os

import anthem

from odoo.addons.base_dj.utils import csv_from_data


@anthem.log
def pre_check_fields(ctx):
    """Pre check fields

        Create a CSV file with all fields in the database.
        Used at the end of the build to see
        which fields must be changed of modules.
        To avoid deletion of fields because
        a field has been moved from a module to another.
    """
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

    data = csv_from_data(fields_data[0], fields_data[0:])

    # We can't create this file in another places, for some reasons:
    #  - We can't use the /tmp directory if we want
    #    to keep the file for test or for launch songs manually.
    #  - We can't use environment variable "ODOO_DATA_PATH",
    #    because the directory /data/odoo is a shared volume on which
    #    the owner is the developper.
    #    And the internal user "odoo" used for launch migration
    #    has no rights to write in this repository.
    #    For information, the migration is launched like this:
    #      https://github.com/camptocamp/docker-odoo-project/
    #      blob/master/bin/docker-entrypoint.sh#L120
    with open('/data/odoo/pre_check_fields.csv', 'w') as fields_csv:
        fields_csv.write(str(data, 'utf-8'))


@anthem.log
def pre(ctx):
    """PRE: migration check fields"""
    env = os.environ.get('RUNNING_ENV')
    # We do the check only in dev mode.
    # To avoid to do the check each times,
    # the check is done only if it's not disabled in environment variables.
    if env == 'dev':
        migration_check_fields = os.environ.get('MIGRATION_CHECK_FIELDS')
        if migration_check_fields != 'True':
            ctx.log_line('If you never check the fields, please do it!')
        else:
            pre_check_fields(ctx)
