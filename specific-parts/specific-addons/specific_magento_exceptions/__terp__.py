# -*- encoding: utf-8 -*-
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
    'name' : 'specific_magento_exceptions',
    'version' : '1',
    'depends' : ['base',
                 'magentoerpconnect',
                 'c2c_magento_negative_stock_choice',
                 'c2c_magento_shipping',
                 'specific_fct',
                 ],
    'author' : 'Camptocamp',
    'description': """Crisis management module for the Debonix launch.
    So many errors issue on synchronisations with Magento (error 500 from magento mainly) that they are all blocked.

    Here we ugly override all the synchronisations to add a exception management which delay the blocking orders/products to the next synchro and document that in a request.

    That code hurts myself but here we have no other choices.

    To remove once the situation has been stabilized on catalog and magento issues.
    """,
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['stock_view.xml',
                  ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
