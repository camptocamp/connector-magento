# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import netsvc


class ProductLink(osv.osv):
    _inherit = 'product.link'

    def get_link_type_selection(self, cr, uid, context=None):
        res = super(ProductLink, self).get_link_type_selection(cr, uid, context)
        if not 'dacrydium_cadeau' in [key[0] for key in res]:
            res.append(('dacrydium_cadeau', 'Gift'))
        return res

    _columns = {
        'type': fields.selection(get_link_type_selection, 'Link type', required=True)
    }

ProductLink()
