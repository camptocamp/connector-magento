# -*- encoding: utf-8 -*-
##############################################################################
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

import logging
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class StockPicking(orm.Model):

    _inherit = "stock.picking"

    _defaults = {
        'number_of_packages': 1,
    }


class StockPickingout(orm.Model):

    _inherit = "stock.picking.out"

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
    }