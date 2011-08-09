# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
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

from osv import osv, fields


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def __init__(self, pool, cr):
        """ Add the stockit status in the available states """
        super(stock_picking, self).__init__(pool, cr)
        stockit_state = ('stockit_confirm', 'Confirmed by Stock-it')
        if stockit_state not in self._columns['state'].selection :
            self._columns['state'].selection.append(stockit_state)
            
    _columns = {
        'stockit_outdated': fields.boolean('Stockit outdated'),
        'stockit_export_date': fields.datetime('Stockit export date')
    }

    def action_cancel(self, cr, uid, ids, context={}):
        res = super(stock_picking, self).action_cancel(cr, uid, ids, context)
        for pick in self.browse(cr, uid, ids):
            if pick.stockit_export_date:
                pick.write({'stockit_outdated': True})
        return res
stock_picking()
