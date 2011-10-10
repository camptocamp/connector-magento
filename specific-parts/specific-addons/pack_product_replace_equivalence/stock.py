# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
#
# Author : Guewen Baconnier (Camptocamp)
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

from osv import osv


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def replace_equivalence(self, cr, uid, ids, context=None):
        """
            If an equivalent product is found on the move product, the replacement is done.
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id and move.picking_id.type == 'out':
                if move.product_id.c2c_debonix_equiv:
                    self.replace_product(cr, uid, move.id, move.product_id.c2c_debonix_equiv.id, context=context)
        return True
    
    def create(self, cr, uid, vals, context=None):
        move_id = super(stock_move, self).create(cr, uid, vals, context=context)
        self.replace_equivalence(cr, uid, move_id, context=context)
        return move_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(stock_move, self).write(cr, uid, ids, vals, context=context)
        self.replace_equivalence(cr, uid, ids, context=context)
        return res


#    def replace_product(self, cr, uid, ids, replace_by_product_id, context=None):

stock_move()
