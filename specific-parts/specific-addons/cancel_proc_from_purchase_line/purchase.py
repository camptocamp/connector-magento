# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
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
##########################################################

from osv import osv, fields


# Cancel properly procurements when the purchase order line is deleted
# Fix from Nan-tic: lp:~nan-tic/openobject-addons/master revno 4809


class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'

    _columns = {
        'origin_procurement_order_id': fields.many2one('mrp.procurement','Procurement'),
    }

    def unlink(self, cr, uid, ids, context=None):
        procurement_ids = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids, context):
            if line.origin_procurement_order_id:
                procurement_ids.append(line.origin_procurement_order_id.id)
        self.pool.get('mrp.procurement').action_cancel(cr, uid, procurement_ids)
        return super(purchase_order_line, self).unlink(cr, uid, ids, context)

purchase_order_line()
