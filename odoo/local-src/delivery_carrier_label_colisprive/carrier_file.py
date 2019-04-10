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
            Add colis prive type
        """
        result = super(carrier_file, self).get_type_selection(
            cr, uid, context=context)
        if 'colisprive' not in result:
            result.append(('colisprive', 'Colisprive'))
        return result

    _columns = {
        'destype': fields.char(string='DestType', size=12),
        'ispcl_withpod': fields.boolean(string='IsPclWithPOD'),
    }


class DeliveryCarrier(orm.Model):
    _inherit = 'delivery.carrier'

    def _get_carrier_type_selection(self, cr, uid, context=None):
        """ Add colisprive carrier type """
        res = super(DeliveryCarrier, self
                    )._get_carrier_type_selection(cr, uid, context=context)
        if 'colisprive' not in res:
            res.append(('colisprive', 'Colisprive'))
        return res

    _columns = {
        'ws_url': fields.char(string='URL for the WS', size=120),
        'ws_username': fields.char(string='WS username', size=24),
        'ws_password': fields.char(string='WS password', size=24),
        'ws_customer_id': fields.char(string='WS Customer ID', size=24),
        'ws_account_id': fields.char(string='WS account ID', size=24),

    }
