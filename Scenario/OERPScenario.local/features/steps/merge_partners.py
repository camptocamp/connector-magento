@then(u'I merge them')
def impl(ctx):
    Model = model('base.partner.merge.automatic.wizard')
    wiz = Model.create({
        'partner_ids': ctx.found_items,
        'dst_partner_id': ctx.found_item,
    })
    wiz.merge_cb()
