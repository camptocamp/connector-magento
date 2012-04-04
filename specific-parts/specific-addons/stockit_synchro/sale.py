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

from osv import osv, fields


class base_sale_payment_type(osv.osv):

    _inherit = 'base.sale.payment.type'

    def get_priority_selection(self, cr, uid, context=None):
        """
        Add a special priority "9" in the packing priorities for stockit
        """
        res = super(base_sale_payment_type, self).get_priority_selection(
            cr, uid, context=context)
        new_selection = list(res)
        # special priority used for stockit,
        # stockit has no other mean to now the product is for a shop
        new_selection.append(('9', 'SHOP'))
        return tuple(new_selection)

    _columns = {
        'packing_priority':
            fields.selection(get_priority_selection, 'Packing Priority')
    }

base_sale_payment_type()
