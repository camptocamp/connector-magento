# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: David BEAL Copyright 2014 Akretion
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
from openerp.tools.translate import _
from openerp.addons.magentoerpconnect import sale
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.magentoerpconnect.backend import magento
from openerp.addons.connector_ecommerce.sale import SpecialOrderLineBuilder
from openerp.addons.connector_ecommerce.unit.sale_order_onchange import (
    SaleOrderOnChange)


@magento(replacing=sale.SaleOrderLineImportMapper)
class SaleOrderLineDiscountMapper(sale.SaleOrderLineImportMapper):
    _model_name = 'magento.sale.order.line'

    @mapping
    def discount_amount(self, record):
        """Remove discount on lines"""
        super(SaleOrderLineDiscountMapper, self).discount_amount(record)
        return {'discount': 0}


@magento(replacing=sale.SaleOrderImportMapper)
class SaleOrderDiscountImportMapper(sale.SaleOrderImportMapper):
    _model_name = 'magento.sale.order'

    def _add_discount_line(self, map_record, values):
        record = map_record.source
        amount = float(record['discount_amount'])
        if not amount:
            return values
        line_builder = self.get_connector_unit_for_model(
            DiscountLineBuilder)
        line_builder.price_unit = amount
        line = (0, 0, line_builder.get_line())
        values['order_line'].append(line)
        return values

    def finalize(self, map_record, values):
        res = super(SaleOrderDiscountImportMapper, self).finalize(map_record, values)
        vals = self._add_discount_line(map_record, values)
        onchange = self.get_connector_unit_for_model(SaleOrderOnChange)
        discount_vals = onchange.play(values, values['magento_order_line_ids'])
        return res


@magento
class DiscountLineBuilder(SpecialOrderLineBuilder):
    """ Return values for a Discount line """
    _model_name = 'magento.sale.order'

    def __init__(self, environment):
        super(DiscountLineBuilder, self).__init__(environment)
        self.product_ref = ('connector_ecommerce', 'product_product_discount')
        self.sequence = 997
