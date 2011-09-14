# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Stock available wizard",
    "version": "1.0",
    "depends": ['base',
                'stock',
                ],
    "author": "Camptocamp",
    "description": """
When an inventory is done, available packings stay available even if after inventory the quantities are insufficient.
This naive wizard cancel availability of all packings and retry to assign them.
    """,
    "website": "http://www.camptocamp.com",
    "category": "Synchronisation",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
                   'wizard/retry_availability_view.xml',
                   ],
    "installable": True,
    "active": False,
}
