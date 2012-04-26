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

from osv import fields
from osv.orm import TransientModel


class stock_partial_picking(TransientModel):

    _inherit = 'stock.partial.picking'

    _columns = {
        'no_confirm': fields.boolean("""Split only.
            Leave the Delivery Orders in "Ready to Process" state."""),
    }

    _defaults = {
        'no_confirm': False
    }

    def do_partial(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
        form = self.browse(cr, uid, ids[0], context=context)
        form_ctx = context.copy()
        if form.no_confirm:
            form_ctx['partial_no_confirm'] = True
        return super(stock_partial_picking, self).do_partial(
            cr, uid, ids, context=form_ctx)

