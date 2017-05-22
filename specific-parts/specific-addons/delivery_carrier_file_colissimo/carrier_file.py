# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Charline Dumontet
#    Copyright 2017 Camptocamp SA
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


class carrier_file(orm.Model):
    _inherit = 'delivery.carrier.file'

    def get_type_selection(self, cr, uid, context=None):
        """
            Add colissimo type
        """
        result = super(carrier_file, self).get_type_selection(
            cr, uid, context=context)
        if 'colissimo' not in result:
            result.append(('colissimo', 'Colissimo'))
        return result


class DeliveryCarrier(orm.Model):
    _inherit = 'delivery.carrier'

    def _get_carrier_type_selection(self, cr, uid, context=None):
        """ Add colissimo type """
        res = super(DeliveryCarrier, self)._get_carrier_type_selection(
            cr, uid, context=context)
        if 'colissimo' not in res:
            res.append(('colissimo', 'Colissimo'))
        return res

    _columns = {
        'product_code': fields.char('Product code', size=4),
        'expeditor_name': fields.char('Expeditor name', size=128),
    }
