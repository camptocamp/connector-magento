# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm
from openerp.tools.translate import _


class MergePartnerAutomatic(orm.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    def _merge(self, cr, uid, partner_ids, dst_partner=None, context=None):
        partner_obj = self.pool['res.partner']
        loc_partner_ids = partner_obj.exists(cr, uid, list(partner_ids),
                                             context=context)
        partners = partner_obj.browse(cr, uid, loc_partner_ids,
                                      context=context)
        # Prevent to merge partners that comes from Magento.
        # This check is simplified, it prevents merging partners from
        # different backends.  A generic check would need to allow
        # merging customer from different backends together.
        if len([partner for partner in partners
                if partner.magento_bind_ids]) > 1:
            raise orm.except_orm(
                _('Error'),
                _('The selected partners cannot be merged together because '
                  'they are linked with different customers on Magento'))

        result = super(MergePartnerAutomatic, self)._merge(
            cr, uid, partner_ids,
            dst_partner=dst_partner,
            context=context
        )
        return result
