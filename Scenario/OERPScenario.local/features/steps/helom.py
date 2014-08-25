# -*- coding: utf-8 -*-
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
