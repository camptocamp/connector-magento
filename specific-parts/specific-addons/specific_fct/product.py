# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
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
from openerp.tools.translate import _


class Product(orm.Model):
    """ Inherit product for small customisations"""

    _inherit = 'product.product'

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}

        # reset the osc_oldid -> it represents the id of the product in the old
        # oscommerce system of debonix
        default['x_magerp_zdbx_osc_oldid'] = False
        default['x_ooor_id'] = False

        return super(Product, self).copy(cr, uid, id,
                                         default=default, context=context)

    def _fix_default_code(self, cr, uid, default_code, context=None):
        if not default_code:
            return default_code
        default_code = default_code.strip()
        if ',' in default_code:
            raise orm.except_orm(
                _('Error'),
                _("The comma character \",\" in the "
                  "reference is forbidden (%s) " % default_code))
        return default_code

    def create(self, cr, uid, vals, context=None):
        if 'default_code' in vals:
            vals['default_code'] = self._fix_default_code(
                cr, uid, vals['default_code'], context=context)
        return super(Product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'default_code' in vals:
            vals['default_code'] = self._fix_default_code(
                cr, uid, vals['default_code'], context=context)
        return super(Product, self).write(cr, uid, ids, vals, context=context)


class product_supplierinfo(orm.Model):
    _inherit = "product.supplierinfo"

    def _calc_min_qty(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        priceinfo_obj = self.pool['pricelist.partnerinfo']
        for suppinfo_id in ids:
            # Retrieve lowest min_quantity
            priceinfo_ids = priceinfo_obj.search(
                cr, uid, [('suppinfo_id', '=', suppinfo_id),
                          ('min_quantity', '!=', False)], limit=1,
                order='min_quantity asc', context=context)
            if len(priceinfo_ids) > 0:
                priceinfo = priceinfo_obj.browse(cr, uid, priceinfo_ids[0],
                                                 context=context)
                result[suppinfo_id] = priceinfo.min_quantity
            else:
                # default value: 1.0
                result[suppinfo_id] = 1.0
        return result

    def _get_suppinfo_from_pricelistinfo(self, cr, uid, ids, context=None):
        suppinfos = []
        for priceinfo in self.pool['pricelist.partnerinfo'].browse(
                cr, uid, ids, context=context):
            suppinfos.append(priceinfo.suppinfo_id.id)
        return list(set(suppinfos))

    _qty_store_dict = {
        'product.supplierinfo':
        (lambda self, cr, uid, ids, c={}: ids,
         ['pricelist_ids'],
         20),
        'pricelist.partnerinfo':
        (_get_suppinfo_from_pricelistinfo,
         ['min_quantity'],
         20)
    }

    _columns = {
        'min_qty': fields.function(
            _calc_min_qty,  type='float', string='Minimal Quantity',
            readonly=True, store=_qty_store_dict,
            help="The minimal quantity to purchase to this supplier, "
                 "expressed in the supplier Product Unit of Measure "
                 "if not empty, in the default unit of measure "
                 "of the product otherwise."),
    }

    def create(self, cr, uid, vals, context=None):
        if not vals.get('origin_country_id', False):
            supplier_id = vals['name']
            partner_obj = self.pool['res.partner']
            origin_country = partner_obj.read(cr, uid,
                                              [supplier_id],
                                              ['origin_country_id'],
                                              context=context)[0]
            if origin_country['origin_country_id']:
                country_id = origin_country['origin_country_id'][0]
                vals['origin_country_id'] = country_id
        return super(product_supplierinfo, self).create(cr, uid,
                                                        vals,
                                                        context=context)
