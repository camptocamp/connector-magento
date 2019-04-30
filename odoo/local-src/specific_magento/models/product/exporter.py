# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class DebonixProductInventoryExporter(Component):
    _inherit = 'magento.product.product.exporter'

    def _get_data(self, binding, fields):
        data = super()._get_data(binding, fields)

        # FIXME: 'manage_stock' is a fields.Selection (even in v7.0)
        # Here even if its value is 'no' we flag data['manage_stock'] to True
        # is it what we want?
        if binding.manage_stock:
            backorders = binding.backorders
            data.update({
                'backorders': self._map_backorders[backorders],
                'is_in_stock': True,
                'use_config_manage_stock': True,
                'manage_stock': True,
                'use_config_min_sale_qty': True,
                'use_config_max_sale_qty': True,
            })
        else:
            data.update({
                'manage_stock': False,
                'use_config_manage_stock': False,
            })
        return data


class DebonixProductExporter(Component):
    """ Products are created on Magento. Export only changes of
    some fields.
    """
    _name = 'magento.debonix.product.product.exporter'
    _inherit = 'magento.exporter'
    _apply_on = ['magento.product.product']
    _usage = 'product.product.exporter'


class DebonixProductExportMapper(Component):
    _name = 'magento.product.product.export.mapper'
    _inherit = 'magento.export.mapper'
    _apply_on = ['magento.product.product']

    direct = [
        ('magento_cost', 'cost'),
    ]


class MagentoBindingProductProductListener(Component):
    _name = 'magento.binding.product.product.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['magento.product.product']

    def on_record_create(self, record, fields=None):
        self._export(record, fields)

    def on_record_write(self, record, fields=None):
        self._export(record, fields)

    def _export(self, record, fields=None):
        """Export only 'magento_cost' field."""
        if 'magento_cost' in fields:
            descr = "Export cost of product {}".format(name)
            record.with_delay().export_record(
                fields=['magento_cost'], description=descr)
