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

from osv import osv, fields


class base_sale_payment_type(osv.osv):
    _inherit = 'base.sale.payment.type'

    def get_priority_selection(self, cr, uid, context=None):
        res = super(base_sale_payment_type, self).get_priority_selection(cr, uid, context=context)
        new_selection = list(res)
        new_selection.append(('9', 'SHOP'))  # special priority used for stockit, stockit has no other mean to now the product is for a shop
        return tuple(new_selection)

    _columns = {
        'packing_priority': fields.selection(get_priority_selection, 'Packing Priority')
    }

base_sale_payment_type()
