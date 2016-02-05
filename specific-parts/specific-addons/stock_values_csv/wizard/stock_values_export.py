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
import unicodecsv


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
            writer = unicodecsv.writer(file_data, encoding='utf-8')
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
            SELECT in_out_summed.product_id,
                   in_out_summed.quantity,
                   COALESCE(in_year.qty, 0)
                       AS in_year_qty,
                   COALESCE(out_year.qty, 0)
                       AS out_year_qty,
                   COALESCE(in_year_1.qty, 0)
                       AS in_year_1_qty,
                   COALESCE(out_year_1.qty, 0)
                       AS out_year_1_qty,
                   COALESCE(in_year_2.qty, 0)
                       AS in_year_2_qty,
                   COALESCE(out_year_2.qty, 0)
                       AS out_year_2_qty
            FROM (
                SELECT product_id, SUM(qty) AS quantity
                FROM (
                    SELECT s_in.product_id AS product_id,
                           s_in.qty AS qty
                    FROM (
                        SELECT SUM(product_qty) AS qty,
                               product_id
                        FROM stock_move
                        WHERE location_id != %(location_id)s
                        AND location_dest_id = %(location_id)s
                        AND state = 'done'
                        AND date <= %(stop_date)s
                        GROUP BY product_id
                    ) AS s_in
                    UNION
                    SELECT s_out.product_id AS product_id,
                           -s_out.qty AS qty
                    FROM (
                        SELECT SUM(product_qty) AS qty,
                               product_id
                        FROM stock_move
                        WHERE location_id = %(location_id)s
                        AND location_dest_id != %(location_id)s
                        AND state = 'done'
                        AND date <= %(stop_date)s
                        GROUP BY product_id
                    ) AS s_out
                ) AS in_out
                INNER JOIN product_product pp
                ON pp.id = in_out.product_id
                INNER JOIN product_template pt
                ON pt.id = pp.product_tmpl_id
                WHERE pt.type = 'product'
                AND pp.active = true
                GROUP BY product_id
                HAVING SUM(in_out.qty) <> 0
            ) AS in_out_summed
            LEFT JOIN (
                SELECT SUM(product_qty) AS qty,
                       product_id
                FROM stock_move
                WHERE location_id != %(location_id)s
                    AND location_dest_id = %(location_id)s
                    AND state = 'done'
                    AND date <= %(stop_date)s
                    AND date > (date %(stop_date)s - INTERVAL '1 YEAR')
                    GROUP BY product_id
            ) AS in_year
            ON in_year.product_id = in_out_summed.product_id
            LEFT JOIN (
                SELECT SUM(product_qty) AS qty,
                       product_id
                FROM stock_move
                WHERE location_id = %(location_id)s
                AND location_dest_id != %(location_id)s
                AND state = 'done'
                AND date <= %(stop_date)s
                AND date > (date %(stop_date)s - INTERVAL '1 YEAR')
                GROUP BY product_id
            ) AS out_year
            ON out_year.product_id = in_out_summed.product_id
            LEFT JOIN (
                SELECT SUM(product_qty) AS qty,
                       product_id
                FROM stock_move
                WHERE location_id != %(location_id)s
                AND location_dest_id = %(location_id)s
                AND state = 'done'
                AND date <= (date %(stop_date)s - INTERVAL '1 YEAR')
                AND date > (date %(stop_date)s - INTERVAL '2 YEARS')
                GROUP BY product_id
            ) AS in_year_1
            ON in_year_1.product_id = in_out_summed.product_id
            LEFT JOIN (
                SELECT SUM(product_qty) AS qty,
                       product_id
                FROM stock_move
                WHERE location_id = %(location_id)s
                AND location_dest_id != %(location_id)s
                AND state = 'done'
                AND date <= (date %(stop_date)s - INTERVAL '1 YEAR')
                AND date > (date %(stop_date)s - INTERVAL '2 YEARS')
                GROUP BY product_id
            ) AS out_year_1
            ON out_year_1.product_id = in_out_summed.product_id
            LEFT JOIN (
                SELECT SUM(product_qty) AS qty,
                       product_id
                FROM stock_move
                WHERE location_id != %(location_id)s
                AND location_dest_id = %(location_id)s
                AND state = 'done'
                AND date <= (date %(stop_date)s - INTERVAL '2 YEARS')
                AND date > (date %(stop_date)s - INTERVAL '3 YEARS')
                GROUP BY product_id
            ) AS in_year_2
            ON in_year_2.product_id = in_out_summed.product_id
            LEFT JOIN (
                SELECT SUM(product_qty) AS qty,
                       product_id
                FROM stock_move
                WHERE location_id = %(location_id)s
                AND location_dest_id != %(location_id)s
                AND state = 'done'
                AND date <= (date %(stop_date)s - INTERVAL '2 YEARS')
                AND date > (date %(stop_date)s - INTERVAL '3 YEARS')
                GROUP BY product_id
            ) AS out_year_2
            ON out_year_2.product_id = in_out_summed.product_id
        """, {'location_id': location_id,
              'stop_date': stop_date})
        return dict([(x[0], list(x[1:])) for x in cr.fetchall()])

    def _get_header(self, cr, uid, ids, context=None):
        return [u'default_code',
                u'name',
                u'brand',
                u'quantity',
                u'in_year',
                u'out_year',
                u'in_year-1',
                u'out_year-1',
                u'in_year-2',
                u'out_year-2',
                u'standard_price',
                u'total',
                u'supplier_price',
                u'total_supplier_price',
                u'cost_price',
                u'total_cost_price',
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
            quantities = products_qty[product.id]
            quantity = quantities[0]
            total = quantity * product.standard_price
            total_cost_price = quantity * product.cost_price

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
                product.product_brand_id.name
            ] + quantities + [
                str(product.standard_price),
                str(total),
                str(supplier_price),
                str(total_supplier_price),
                str(product.cost_price),
                str(total_cost_price),
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
