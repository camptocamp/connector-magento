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
    'name' : 'debonix_chart',
    'version' : '1.0',
    'depends' : ['account','l10n_fr'],
    'author' : 'Camptocamp',
    'description': """Debonix custom account chart""",
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['accounts.xml'],
    'category':'Account Charts',
    'demo_xml': [],
    'installable': True,
    'active': False,
}