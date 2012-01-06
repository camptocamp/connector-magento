# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
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
    'name' : 'Cancel procurement on purchase line unlink',
    'version' : '1',
    'depends' : ['base',
                 'mrp',
                 'purchase',
                 'c2c_smart_mrp_purchase',
                 ],
    'author' : 'Camptocamp',
    'description': """
    Removing a purchase order line does not cancel procurements.
    This crappy module allows that, but by overriding a lot of methods, because methods are too cluttered in v5.
    Do not reproduce that in current versions!

    https://bugs.launchpad.net/openobject-addons/+bug/725860
    """,
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['purchase_view.xml',
                   'wizard.xml',
                  ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
