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

from osv import fields, osv


class stock_picking(osv.osv):

    _inherit = 'stock.picking'

    _columns = {
        'cash_on_delivery_amount':
            fields.float('Cash on delivery amount',
                         help="Put the amount to be used for the "
                              "packing cash on delivery with chronopost."),
        'cash_on_delivery_amount_untaxed':
            fields.float('Cash on delivery amount untaxed',
                         help="Put the untaxed amount to be used "
                              "for the packing cash on delivery "
                              "with chronopost."),
    }

    def write(self, cr, uid, ids, vals, context=None):
        #cash on delivery must only apply on the first packing
        if 'backorder_id' in vals:
            vals['cash_on_delivery_amount'] = 0.0
            vals['cash_on_delivery_amount_untaxed'] = 0.0
        return super(stock_picking, self).write(
            cr, uid, ids, vals, context=context)

stock_picking()
