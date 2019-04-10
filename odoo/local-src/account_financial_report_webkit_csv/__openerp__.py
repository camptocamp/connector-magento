# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Add CSV export to accounting reports',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA',
    'category': 'Generic Modules/Accounting',
    'description': """

    This module adds CSV export to the following accounting reports:
        - partner balance

    """,
    'depends': ['account_financial_report_webkit'],
    'data': [
        'wizard/partner_balance_wizard_view.xml',
    ],
    'active': False,
    'installable': True,
}
