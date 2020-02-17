# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Magentoerpconnect Refund',
    'version': '0.1',
    'category': 'Connector',
    'license': 'AGPL-3',
    'description': """
    This module is based on sale_credit_note.
    It synchonizes the Magento credit memo.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'magentoerpconnect',
        'crm_claim_rma',
        'sale_credit_note',
        ],
    'data': [
        'wizard/new_credit_memo_view.xml',
        'wizard/new_credit_note_view.xml',
        'invoice_view.xml',
        'sale_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
}
