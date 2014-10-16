# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright 2011 Camptocamp SA
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


from openerp.osv import orm, fields


class ResPartner(orm.Model):
    "Inherit partner for small customisations"
    _inherit = 'res.partner'

    _columns = {
        'siret': fields.char('Siret', size=14),
    }

    _defaults = {
        'lang': 'fr_FR',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}

        default['ref'] = False

        return super(ResPartner, self).copy(
            cr, uid, id, default=default, context=context)

