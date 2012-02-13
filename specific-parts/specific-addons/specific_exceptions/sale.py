# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2012 Camptocamp SA (http://www.camptocamp.com)
#   @author Guewen Baconnier
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields


class sale_order(osv.osv):
    _inherit = "sale.order"

    LOW_MARKUP_RATE = 5.0

    _columns = {
        'skip_exceptions': fields.boolean('Bypass Exceptions')
    }

    def add_custom_order_exception(self, cr, uid, ids, order, exceptions, *args):
        if order.skip_exceptions:
            return False
        self.detect_customer_blocked(cr, uid, order, exceptions)
        self.detect_markup_rate_too_low(cr, uid, order, exceptions)
        for order_line in order.order_line:
            self.detect_not_in_production(cr, uid, order_line, exceptions)
        return exceptions

    def detect_not_in_production(self, cr, uid, order_line, exceptions):
        if order_line.product_id and order_line.product_id.state != 'sellable':
            self.__add_exception(cr, uid, exceptions, 'excep_not_in_production')

    def detect_markup_rate_too_low(self, cr, uid, order, exceptions):
        if order.markup_rate <= self.LOW_MARKUP_RATE:
            self.__add_exception(cr, uid, exceptions, 'excep_markup_rate_too_low')

    # glue with module c2c_block_customer
    # the workflow modification of the module c2c_block_customer is replaced
    # by the one of sale_exceptions and not restored intentionnaly because it
    # is not any more necessary as the workflow is blocked by sale_exceptions
    def detect_customer_blocked(self, cr, uid, order, exceptions):
        if not self.test_blocked(cr, uid, [order.id]):
            self.__add_exception(cr, uid, exceptions, 'excep_customer_blocked')

sale_order()
