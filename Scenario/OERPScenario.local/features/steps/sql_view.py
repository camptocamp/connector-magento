# -*- coding: utf-8 -*-

from support import *
from support.tools import model


@step('I create a SQL view "{sql_name}" named "{name}" with definition')
def impl(ctx, name, sql_name):
    assert_true(ctx.text)
    definition = ctx.text
    SQLView = model('sql.view')
    view = SQLView.search([('sql_name', '=', sql_name)])
    values = {'name': name,
              'sql_name': sql_name,
              'definition': definition,
              }
    if view:
        SQLView.write(view, values)
    else:
        SQLView.create(values)
