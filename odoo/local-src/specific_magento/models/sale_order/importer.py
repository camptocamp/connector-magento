# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo.addons.connector_magento.models.sale_order.importer import (
    SaleOrderImportMapper,
)


class DebonixSaleOrderImporter(Component):
    _inherit = 'magento.sale.order.importer'
    _apply_on = ['magento.sale.order']

    def run(self, external_id, force=False):
        # eagerly return if the sales order exists,
        # we don't even need to read the data on Magento
        if self.binder.to_internal(external_id):
            return _('Already imported')
        return super().run(external_id, force=force)

    def _merge_sub_items(self, product_type, top_item, child_items):
        # special type for Debonix for Magento, should be considered as
        # configurable
        if product_type == 'debadvancedconfigurable':
            product_type = 'configurable'
        return super()._merge_sub_items(product_type, top_item, child_items)


class DebonixSaleOrderImportMapper(Component):
    _inherit = 'magento.sale.order.mapper'

    direct = (SaleOrderImportMapper.direct +
              [('sms_phone', 'sms_phone'),
               ('po_number', 'client_order_ref'),
               ]
              )

    @mapping
    def analytic_account(self, record):
        code = record['analytic_code']
        account = self.env['account.analytic.account'].search(
            [('code', '=', code)],
            limit=1,
        )
        if account:
            return {'project_id': account.id}

    @mapping
    def transaction_id(self, record):
        if record.get('payment'):
            transaction_id = (record['payment']['last_trans_id'] or
                              record['increment_id'])
            return {'transaction_id': transaction_id}

    def _add_fidelity_line(self, map_record, values):
        record = map_record.source
        amount = float(record.get('base_fidelity_currency_amount') or 0.)
        if not amount:
            return values
        line_builder = self.component_by_name(
            'magento.order.line.fidelity.builder')
        line_builder.price_unit = amount
        line_builder.points = record['fidelity_points_balance']
        line = (0, 0, line_builder.get_line())
        values['order_line'].append(line)
        return values

    def _add_admin_costs(self, map_record, values):
        record = map_record.source
        amount = float(record.get('base_xipaymentrules_fees_amount') or 0.)
        if not amount:
            return values
        line_builder = self.component_by_name(
            'magento.order.line.admincosts.builder')
        line_builder.price_unit = amount
        line = (0, 0, line_builder.get_line())
        values['order_line'].append(line)
        return values

    def finalize(self, map_record, values):
        values.setdefault('order_line', [])
        values = self._add_fidelity_line(map_record, values)
        values = self._add_admin_costs(map_record, values)
        return super().finalize(map_record, values)


# TODO We will not migrate it for the moment and keep it in point of attention
# from openerp.addons.connector.unit.mapper import ImportMapChild
# @magento_debonix
# class LineMapChild(ImportMapChild):
#     """ Customize the mapping of sales order lines.

#     Delete sale order lines where the product is a component of a BoM
#     and have a 0.0 price.

#     We have to do that because Magento send the pack and his components
#     in the sale order.

#     And we don't want the components in the sales order, they are added
#     in the delivery order with sale_bom_split.

#     """
#     _model_name = 'magento.sale.order.line'

#     def format_items(self, items_values):
#         items = items_values[:]
#         for item in items_values:
#             product_id = item['product_id']
#             if product_id:
#                 # search if product is a BoM if it is, loop on other products
#                 # to search for his components to drop
#                 product = self.session.browse('product.product', product_id)

#                 if not product.bom_ids:
#                     continue

#                 # search the products components of the BoM (always one
#                 # level when imported from magento)
#                 bom_prod_ids = set()
#                 for bom in product.bom_ids:
#                     bom_prod_ids |= set(
#                         [bom_line.product_id.id for bom_line in bom.bom_lines]
#                     )

#                 for other_item in items[:]:
#                     if other_item['product_id'] == product_id:
#                         continue

#                     # remove the lines of the bom only when the price is 0.0
#                     # because we don't want to remove a component that
#                     # is ordered alone
#                     if other_item['product_id'] in bom_prod_ids and \
#                        not other_item['price_unit']:
#                         items.remove(other_item)

#         return [(0, 0, item) for item in items]
