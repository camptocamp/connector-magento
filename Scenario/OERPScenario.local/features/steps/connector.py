# -*- coding: utf-8 -*-
from support import *
from support.tools import model


@given('I press the button "{button}"')
def impl(ctx, button):
    backend = ctx.found_item
    assert backend
    getattr(backend, button)()


@given('I recompute the magento stock quantities without export')
def impl(ctx):
    backend = ctx.found_item
    assert backend
    backend.update_product_stock_qty(context={'connector_no_export': True})
