# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Yannick Vaucher. Copyright 2011 Camptocamp SA
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

class AccountAccount(osv.osv):
        "Inherit account to add can be part of followup"
        _inherit = 'account.account'

        _columns = {
                    'be_follow_up':
                        fields.boolean('Do not chase payments on this account',
                                           help="If checked, this account will be not "
                                                "part of the chasing payment report "),
                }
