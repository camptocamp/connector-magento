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


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _display_address(self, cr, uid, address, without_company=False,
                         context=None):
        """ Hides the company name (parent name) if it is identical
        to the address name or if the parent comes from Magento and
        is not considered as a company.
        """
        parent = address.parent_id
        address_company = False
        if parent:
            name = (address.name or '').strip().lower()
            parent_name = (parent.name or '').strip().lower()
            bindings = parent.magento_bind_ids
            if name == parent_name:
                without_company = True
            elif (bindings and name and
                    not any(bind.consider_as_company for bind in bindings)):
                # comes from Magento and is not considered as a company,
                # only display the address' name
                without_company = True

        if address.company:
            # field added by magentoerpconnect on the addresses,
            # when a customer has filed a company on the address,
            # he maybe want to deliver to another company than
            # his one, so we display the address company
            address_company = True
            if address.name:
                without_company = True

        disp_address = super(res_partner, self)._display_address(
            cr, uid, address, without_company=without_company, context=context)

        if address_company:
            disp_address = '%s\n' % address.company + disp_address
        return disp_address
