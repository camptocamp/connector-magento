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

from openerp.osv import orm, fields


class carrier_file(orm.Model):
    _inherit = 'delivery.carrier.file'

    def get_type_selection(self, cr, uid, context=None):
        result = super(carrier_file, self).get_type_selection(
            cr, uid, context=context)
        if 'chronopost' not in result:
            result.append(('chronopost', 'Chronopost'))
        if 'chronorelais' not in result:
            result.append(('chronorelais', 'Chronorelais'))
        return result

    _columns = {
        'subaccount_number':
            fields.char('Sub-Account Number',
                        size=3,
                        help="Subaccount number of the company. "
                             "This number is output at the 3 first "
                             "positions on the csv."),
        'chronopost_code':
            fields.char('Chronopost Code',
                        size=3,
                        required=False,
                        help="The Chronopost code is output on "
                             "the packing csv chronopost file"),
        'saturday_delivery_code':
            fields.char('Saturday Delivery Code',
                        size=1, required=True,
                        help="Chronopost code for the saturday deliveries. "
                             "which will be output in the carrier files"),
        'chronopost_insurance':
            fields.float('Chronopost insurance amount'),
    }

    _defaults = {
        'saturday_delivery_code': 'L',
    }
