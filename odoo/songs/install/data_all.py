# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.loaders import load_csv


""" Data loaded in all modes

The data loaded here will be loaded in the 'sample' and
'full' modes.

"""


@anthem.log
def import_payment_terms(ctx):
    """ Importing payment terms """
    payment_term_model = ctx.env['account.payment.term'].with_context(
        {'tracking_disable': True}
    )
    payment_term_line_model = ctx.env[
        'account.payment.term.line'
    ].with_context({'tracking_disable': True})
    load_csv(ctx, payment_term_model, 'install/account_payment_term.csv')

    # Remove default balance line created when payment term is created
    imported_payment_terms_data = ctx.env['ir.model.data'].search(
        [('module', '=', '__setup__'), ('model', '=', 'account.payment.term')]
    )
    ctx.env['account.payment.term'].browse(
        imported_payment_terms_data.mapped('res_id')
    ).write({'line_ids': [(5, False)]})

    # Import payment term lines
    load_csv(
        ctx, payment_term_line_model, 'install/account_payment_term_line.csv'
    )


@anthem.log
def import_partner_categories(ctx):
    """ Importing partner categories """
    partner_category_model = ctx.env['res.partner.category'].with_context(
        {'tracking_disable': True}
    )
    load_csv(ctx, partner_category_model, 'install/res_partner_category.csv')
    load_csv(
        ctx, partner_category_model, 'install/res_partner_category_parents.csv'
    )


@anthem.log
def import_partner_titles(ctx):
    """ Importing partner titles """
    partner_title_model = ctx.env['res.partner.title'].with_context(
        {'tracking_disable': True}
    )
    load_csv(ctx, partner_title_model, 'install/res_partner_title.csv')


@anthem.log
def main(ctx):
    """ Loading data """
    import_payment_terms(ctx)
    import_partner_categories(ctx)
    import_partner_titles(ctx)
