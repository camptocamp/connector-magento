# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Retry to assign assigned packings on inventory",
    "version": "1.0",
    "depends": ['stock',
                'packing_priority_on_payment_type'],
    "author": "Camptocamp",
    "description": """
When an inventory is done, available packings stay available even if after inventory the quantities are insufficient.
This naive wizard cancel availability of all packings and retry to assign them.
    """,
    "website": "http://www.camptocamp.com",
    "category": "Others",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
                   'wizard/retry_availability_view.xml',
                   ],
    'installable': False,
    "active": False,
}
