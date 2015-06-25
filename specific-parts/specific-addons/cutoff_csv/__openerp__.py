# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2009-2014 Camptocamp SA
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

{'name': 'Cut-off Reports',
 'version': '1.0',
 'depends': ['sale',
             'purchase'],
 'author': 'Camptocamp',
 'description': """2 cut-off reports:
     * "Outgoing cut-off": reports all uninvoiced products which were sent
       to the customer, but not yet invoiced (drop-shipping items are
       not accounted for).
     * "Incoming cut-off": reports all uninvoiced products which were
       received but not yet invoiced.""",
 'category': 'Generic Modules/Accounting',
 'data': ['wizard/cutoff_view.xml'],
 'installable': True,
 }
