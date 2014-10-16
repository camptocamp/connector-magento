# -*- coding: utf-8 -*-
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')

@step('I create a note in each crm_claim to save old stage')
def impl(ctx):
    """
    For each crm claim using an old crm claim stage, copy the name of stage in
    a message note attached on crm claim
    """
    new_stage_data = model('ir.model.data').browse(
            [('model', '=', 'crm.claim.stage'),
             ('module', '=', 'crm_claim'),
             ('name', 'in', ['stage_claim1',
                             'stage_claim2',
                             'stage_claim3',
                             'stage_claim5'])])

    new_stage_ids = [data.res_id for data in new_stage_data]

    old_claims = model('crm.claim').browse([('stage_id', 'not in', new_stage_ids)])
    for claim in old_claims:
        values = claim.stage_id.name
        ctx.client.execute('crm.claim', 'message_post', claim.id, values)
