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

from osv import fields, osv
from tools.translate import _

class ResCompany(osv.osv):
    """override company to add a list of titles for which we hide the partner name on reports"""
    _inherit = "res.company"
    _columns = {
                'report_hide_partner_title_ids':fields.many2many(
                       'res.partner.title',
                       'report_hide_partner_title_rel',
                       'company_id',
                       'res_partner_title_id',
                       'Hide the partner name on reports for these titles',
                       help='''For the partners corresponding to the selected titles,
only the contact name will be displayed on report, the partner name will be hidden.
Useful to avoid the print of 2 lines on the reports for certain categories of partners.''',
                       ),
    }
ResCompany()
