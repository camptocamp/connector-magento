# -*- coding: utf-8 -*-
import os
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

@given(u'I set RML header to company with oid "{comp_oid}" using "{csvfile}" file')
def impl(ctx, comp_oid, csvfile):
    comp = model('res.company').get(comp_oid)
    tmp_path = ctx.feature.filename.split(os.path.sep)
    tmp_path = tmp_path[1: tmp_path.index('features')] + ['data', csvfile]
    tmp_path = [str(x) for x in tmp_path]
    path = os.path.join('/', *tmp_path)
    assert os.path.exists(path)
    with open(path) as header_file:
        header = header_file.read()
        comp.write({'rml_header': header})

@given(u'I reassign cron "{cron_name}" from user "{origin_user}" to "{new_user}"')
def impl(ctx, cron_name, origin_user, new_user):
    new_user = model('res.users').get([('login', '=', new_user)])
    origin_user = model('res.users').get([('login', '=', origin_user)])
    cron = model('ir.cron').get(
        [
            ('name', '=', cron_name),
            ('user_id', '=', origin_user.id),
        ],
        context={'active_test': False}
    )
    assert_true(cron, 'no cron found')
    cron.write({'user_id': new_user.id})

@given(u'I duplicate cron "{cron_name}" and assign it to user "{new_user}" '
       'with a delay of "{delay:d}" seconds')
def imp(ctx, cron_name, new_user, delay):
    new_user = model('res.users').get([('login', '=', new_user)])
    cron = model('ir.cron').browse(
        [
            ('name', '=', cron_name),
        ],
        context={'active_test': False}
    )
    assert_true(cron, 'no cron found')
    new_cron = cron[0].copy()
    new_cron.write({'user_id': new_user.id})
    exec_time = new_cron.nextcall
    exec_time = datetime.datetime.strptime(exec_time,
                                           DEFAULT_SERVER_DATETIME_FORMAT)
    new_time = exec_time + datetime.timedelta(seconds=delay)
    new_cron.write({'nextcall': new_time})

@then(u'I force following rule domain')
def impl(ctx):
    assert_true(ctx.found_item)
    rule = ctx.found_item
    domain = ctx.text
    domain.strip()
    assert_true(domain, 'No domain')
    rule.write({'domain_force': domain})
