# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

import time
import datetime
from openerp.report import report_sxw


class Order(report_sxw.rml_parse):
    _name = 'report.sale.order_custom'

    def __init__(self, cr, uid, name, context):
        super(Order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'estimated_delivery_date': self._get_estimated_delivery_date,
            'show_discount': self._show_discount,
        })

    def _get_estimated_delivery_date(self, order_obj):
        """Compute the estimated delivery date as : take the highest
        delivery lead time in order lines and add it to the order date
        """
        max_delay = 0
        for line in order_obj.order_line:
            if line.delay > max_delay:
                max_delay = line.delay

        max_date = datetime.date.fromtimestamp(
            time.mktime(time.strptime(order_obj.date_order, "%Y-%m-%d")))
        max_date = max_date + datetime.timedelta(days=max_delay)

        return max_date

    def _show_discount(self, uid, context=None):
        cr = self.cr
        try: 
            group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]

report_sxw.report_sxw('report.sale.order_custom',
                      'sale.order',
                      'addons/specific_report/report/sale_order.rml',
                      parser=Order)
