# -*- coding: utf-8 -*-
from support import *
from support.tools import model


@given('I need an Elasticsearch template named "{name}" on host with oid "{host_xmlid}" having template')
def impl(ctx, name, host_xmlid):
    assert ctx.text
    template = ctx.text
    IndexTemplate = model('elasticsearch.index.template')
    record = IndexTemplate.get([('name', '=', name)])
    host = model('elasticsearch.host').get(host_xmlid)
    assert host
    values = {'template': template, 'host_id': host.id}
    if record:
        record.write(values)
    else:
        values['name'] = name
        record = IndexTemplate.create(values)

    record.refresh_template()
