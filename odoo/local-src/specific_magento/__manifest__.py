# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Magento Connector Customization',
    'version': '12.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Connector',
    'depends': [
        'connector_magento',
        'mrp',
        'stock_account',
        'product_brand',
        'product_state',
        'base_transaction_id',
        # TODO: review dependencies
        # 'delivery_carrier_file_chronopost',    # local, to migrate?
        # 'product_cost_incl_bom',       # OCA, to migrate from 7.0?
        # 'packing_product_change',      # local, to migrate?
        # 'l10n_fr_intrastat_product',   # OCA, to migrate from 11.0?
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/product_product.xml',
        'views/magento_product_product.xml',
        'views/magento_backend.xml',
    ],
    'installable': True,
}
