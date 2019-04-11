# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Debonix Supplier Invoice EDI',
 'version': '1',
 'depends': [
     'crm_claim_rma',
     'specific_fct',
 ],
 'author': 'Camptocamp SA',
 'description': """import supplier invoices from supplier SOGEDESCA""",
 'website': 'http://www.camptocamp.com',
 'data': [
     'data/crm_case_categ.xml',
     'data/ir_cron.xml',
 ],
 'demo': [
     'demo/demo.xml'
 ],
 'installable': False,
 }
