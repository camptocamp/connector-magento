# -*- coding: utf-8 -*-
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')

@step('I want to modify all the delivery methods linked with {partner_name} partner')
def impl(ctx, partner_name):
    partner = model('res.partner').browse(['name = %s' % partner_name], limit=1)
    assert partner
    carriers = model('delivery.carrier').browse(['partner_id = %s' % partner[0].id])
    ctx.found_items = carriers


@step('I set their values to')
def impl(ctx):
    values = dict(ctx.table)
    for k, v in values.iteritems():
        if 'by oid:' in v:
            module, xmlid = v[7:].strip().split('.')

            _model, id = model('ir.model.data').get_object_reference(module, xmlid)
            values[k] = id
    ctx.found_items.write(values)
