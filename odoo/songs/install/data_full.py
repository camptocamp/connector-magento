# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.loaders import load_csv


""" File for full (production) data

These songs will be called on integration and production server at the
installation.

"""


@anthem.log
def import_partner(ctx):
    """ Importing partners """
    partner_model = ctx.env['res.partner'].with_context(
        {'tracking_disable': True}
    )
    load_csv(ctx, partner_model, 'install/res_partner.csv')


@anthem.log
def import_partner_description(ctx):
    """ Importing partner descriptions """
    partner_model = ctx.env['res.partner'].with_context(
        {'tracking_disable': True}
    )
    load_csv(ctx, partner_model, 'install/res_partner_descriptions.csv')


@anthem.log
def import_partner_parent(ctx):
    """ Importing partner parents """
    partner_model = ctx.env['res.partner'].with_context(
        {'tracking_disable': True}
    )
    load_csv(ctx, partner_model, 'install/res_partner_parents.csv')


@anthem.log
def main(ctx):
    """ Loading full data """
    import_partner(ctx)
    import_partner_description(ctx)
    import_partner_parent(ctx)
