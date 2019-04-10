# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openupgradelib.openupgrade import logged_query


def update_module_moved_models(cr, models, old_module, new_module):
    """ Update metadata for models moved to another module """

    # TODO: If that function works correctly on many projects,
    # TODO: see to propose it on openupgradelib.

    for model in models:
        query = 'SELECT id FROM ir_model WHERE name = %s'
        cr.execute(query, [model])
        row = cr.fetchone()
        if row:
            model_id = row[0]

            # Update the XML ID of the model
            query = """
                UPDATE
                    ir_model_data
                SET
                    module = %s
                WHERE
                    module = %s
                AND
                    model = 'ir.model'
                AND
                    res_id = %s
            """
            logged_query(cr, query, (new_module, old_module, model_id))

            # Update the XML ID of the fields of the model
            query = """
                UPDATE
                    ir_model_data
                SET
                    module = %s
                WHERE
                    module = %s
                AND
                    model = 'ir.model.fields'
                AND
                    res_id IN (
                        SELECT
                            id
                        FROM
                            ir_model_fields
                        WHERE
                            model_id = %s
                    )
            """
            logged_query(cr, query, (new_module, old_module, model_id))
