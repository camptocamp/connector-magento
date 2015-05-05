# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#    Copyright 2012 Camptocamp SA
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
###############################################################################

import time
import StringIO
import base64

from openerp.osv import orm, fields
from ..unicode_csv.writer import UnicodeWriter


class StockValuesExport(orm.TransientModel):
    _name = 'stock.values.detail.export'
    _description = 'Export Stock values details for a location'

    _columns = {
        'location_id': fields.many2one('stock.location', 'Location',
                                       required=True),
        'stop_date': fields.datetime('Date',
                                     help="Keep empty to export details at "
                                          "current date."),
        'data': fields.binary('CSV', readonly=True),
        'state': fields.selection([('draft', 'Draft'),
                                   ('done', 'Done')],
                                  string='State'),
    }

    _defaults = {
        'state': 'draft',
    }

    def action_manual_export(self, cr, uid, ids, context=None):
        rows = self.get_data(cr, uid, ids, context)

        file_data = StringIO.StringIO()
        try:
            writer = UnicodeWriter(file_data)
            writer.writerows(rows)
            file_value = file_data.getvalue()
            self.write(cr, uid, ids,
                       {'data': base64.encodestring(file_value),
                        'state': 'done'},
                       context=context)
        finally:
            file_data.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }

    def _get_product_qty(self, cr, uid, ids, location_id, stop_date=None,
                         context=None):
        stop_date = stop_date or time.strftime('%Y-%m-%d %H:%M:%S')
        cr.execute("""
                    SELECT pp.id,
                           SUM(qty) AS qty
                      FROM (SELECT p.id AS product_id,
                                   t.id AS template_id,
                                   s_in.qty
                              FROM (SELECT SUM(product_qty) AS qty,
                                           product_id
                                      FROM stock_move
                                     WHERE location_id != %(location_id)s
                                       AND location_dest_id = %(location_id)s
                                       AND state = 'done'
                                       AND date <= %(stop_date)s
                                     GROUP BY product_id) AS s_in
                             INNER JOIN product_product p
                                ON p.id = s_in.product_id
                             INNER JOIN product_template t
                                ON t.id = p.product_tmpl_id
                             UNION
                            SELECT p.id AS product_id,
                                   t.id AS template_id,
                                   -s_out.qty AS qty
                              FROM (SELECT SUM(product_qty) AS qty,
                                           product_id
                                      FROM stock_move
                                     WHERE location_id = %(location_id)s
                                       AND location_dest_id != %(location_id)s
                                       AND state = 'done'
                                       AND date <= %(stop_date)s
                                     GROUP BY product_id) AS s_out
                             INNER JOIN product_product p
                                ON p.id = s_out.product_id
                             INNER JOIN product_template t
                                ON t.id = p.product_tmpl_id) AS in_out
                     INNER JOIN product_template pt
                        ON pt.id = in_out.template_id
                     INNER JOIN product_product pp
                        ON pp.id = in_out.product_id
                     WHERE pt.type = 'product'
                       AND pp.active = true
                     GROUP BY pp.id
                    HAVING SUM(qty) <> 0""",
                   {'location_id': location_id,
                    'stop_date': stop_date,
                    })
        return dict(cr.fetchall())

    def _get_header(self, cr, uid, ids, context=None):
        return [u'default_code',
                u'name',
                u'brand',
                u'quantity',
                u'standard_price',
                u'total',
                u'supplier_price',
                u'total_supplier_price',
                ]

    def _get_rows(self, cr, uid, ids, products_qty, context=None):
        """
        Return list to generate rows of the CSV file
        @param products_qty: dict where keys = product_id and
                             values = quantity in location
        """
        product_obj = self.pool.get('product.product')
        rows = []
        for product in product_obj.browse(cr, uid, products_qty.keys(),
                                          context=context):
            quantity = products_qty[product.id]
            total = quantity * product.standard_price

            supplier_price = 0.0
            if product.seller_ids:
                seller = product.seller_ids[0]
                for pricelist in seller.pricelist_ids:
                    if pricelist.min_quantity < 2:
                        supplier_price = pricelist.price
                        break

            total_supplier_price = quantity * supplier_price

            row = [
                product.default_code,
                product.name,
                product.product_brand_id.name,
                str(quantity),
                str(product.standard_price),
                str(total),
                str(supplier_price),
                str(total_supplier_price),
            ]
            rows.append(row)
        return rows

    def get_data(self, cr, uid, ids, context=None):
        context = context or {}
        context['lang'] = 'fr_FR'

        form = self.browse(cr, uid, ids[0], context=context)

        products_qty = self._get_product_qty(cr, uid, ids, form.location_id.id,
                                             form.stop_date, context=context)

        rows = []
        rows.append(self._get_header(cr, uid, ids, context=context))
        rows.extend(self._get_rows(cr, uid, ids, products_qty,
                                   context=context))

        return rows