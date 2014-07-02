# -*- coding: utf-8 -*-
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')


@step('I recompute complete_name on stock.location')
def impl(ctx):
    Location = model('stock.location')
    locations = Location.search([])
    for location_id in locations:
        if location_id == 11:  # hang on Stock... let continue
            continue
        location = Location.get(location_id)
        location.write({'name': location.name})
