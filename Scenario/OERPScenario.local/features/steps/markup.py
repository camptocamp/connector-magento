# -*- coding: utf-8 -*-
from contextlib import closing
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')


@step('I recompute markup rate on products')
def impl(ctx):
    """
    Recompute sale_markup on products
    """
    all_products = model('product.product').browse([])

    for product in all_products:
        values = {}
        sale_price = product.list_price
        cost_price = product.cost_price
        margin = product.commercial_margin

        true_margin = sale_price - cost_price
        if abs(true_margin - margin) > 0.01:
            values['commercial_margin'] = true_margin

        markup = product.markup_rate

        if sale_price:
            true_markup = true_margin / sale_price
            if abs(true_markup * 100.0 - markup) > 0.01:
                values['markup_rate'] = true_markup * 100.0

        if values:
            product.write(values)
