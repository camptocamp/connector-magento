# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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


class stock_picking(orm.Model):

    _inherit = "stock.picking"

    def get_selection_priority(self, cr, uid, context=None):
        """ Add a Shop priority.

        This is a special priority for Stockit

        """
        selection = super(stock_picking, self).get_selection_priority(
            cr, uid, context=context)
        selection.append(('9', 'Shop'))
        return selection

    _columns = {
        'stockit_outdated': fields.boolean('Stockit outdated'),
        'stockit_export_date': fields.datetime('Stockit export date'),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        res = super(stock_picking, self).action_cancel(cr, uid, ids, context)
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.stockit_export_date:
                pick.write({'stockit_outdated': True})
        return res
