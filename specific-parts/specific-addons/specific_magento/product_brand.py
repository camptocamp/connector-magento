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

from openerp.osv import orm, fields


# TODO : when importing a product; if brand is not known, get it from
# API

class magento_product_brand(orm.Model):
    _name = 'magento.product.brand'
    _inherit = 'magento.binding'
    _inherits = {'product.brand': 'openerp_id'}
    _description = 'Magento Product Brand'

    _columns = {
        'openerp_id': fields.many2one('product.brand',
                                      string='Product Brand',
                                      required=True,
                                      ondelete='cascade'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A product brand with same ID on Magento already exists.'),
    ]


class product_brand(orm.Model):
    _inherit = 'product.brand'

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.product.brand', 'openerp_id',
            string="Magento Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['magento_bind_ids'] = False
        return super(product_brand, self).copy_data(cr, uid, id,
                                                    default=default,
                                                    context=context)
