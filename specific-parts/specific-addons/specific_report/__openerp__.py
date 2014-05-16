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

{'name': 'Specific Reports',
 'version': '1.0',
 'depends': ['sale',
             'purchase',
             'report_webkit',
             'packing_product_change',
             'magentoerpconnect',
             ],
 'author': 'Camptocamp',
 'description': """Debonix Reports""",
 'category': 'Generic Modules/Accounting',
 'data': ['report/data/bank_statement_webkit_header.xml',
          'report.xml',
          'company_view.xml',
          'account_view.xml',
          ],
 'installable': True,
}
