# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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

{'name': "Advanced Reconcile with TID",
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': ['account_advanced_reconcile'],
 'description': """
 Add specific reconciliation method which searches by:
 On: *payment*  => *invoice*
     credit     => debit
     partner_id => partner_id
     ref        => name or ref or
                   "tid_" + name or "tid_mag_" + name or
                   "tid_" + ref or "tid_mag_" + ref or

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['easy_reconcile_view.xml'],
 'test': [],
 'images': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
}
