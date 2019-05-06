# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    external_to_m2o, mapping, only_create)
from odoo.addons.connector.exception import MappingError

from odoo.addons.connector_magento.models.product.importer import (
    ProductImportMapper)


class DebonixProductImporter(Component):
    _inherit = 'magento.product.product.importer'

    def _import_dependencies(self):
        """Import the dependencies for the record."""
        super()._import_dependencies()
        record = self.magento_record
        if record.get('marque'):
            self._import_dependency(record['marque'],
                                    'magento.product.brand')
        if record.get('openerp_supplier_name'):
            self._import_dependency(record['openerp_supplier_name'],
                                    'magento.supplier')
        if record.get('universe'):
            self._import_dependency(record['universe'],
                                    'magento.product.universe')

    def _get_binding(self):
        """Return the binding from the Magento id

        Debonix wants the products mapped from the SKU.
        Still, the Magento ID should be stored correctly and
        used as reference for the synchronizations.

        When we import a product, we search if we have a binding
        for a SKU so if the Magento ID for this SKU is wrong,
        we have a chance to correct it.
        """
        record = self.magento_record
        magento_pp_model = self.env['magento.product.product'].with_context(
            active_test=False)
        bindings = magento_pp_model.search(
            [('default_code', '=', record['sku'])],
        )
        if bindings:
            return bindings[0]
        return super()._get_binding()

    def _must_skip(self):
        """ Hook called right after we read the data from the backend.

        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).

        If it returns None, the import will continue normally.

        :returns: None | str | unicode
        """
        if self.magento_record['type_id'] == 'debadvancedconfigurable':
            return _('The configurable product is not imported in Odoo, '
                     'because only the simple products are used in the sales '
                     'orders.')
        return super()._must_skip()


class ProductSupplierInfoMapChild(Component):
    _name = 'magento.map.child.import.product.supplierinfo'
    _inherit = 'base.map.child.import'
    _apply_on = ['product.supplierinfo']

    def format_items(self, items_values):
        items = []
        for item in items_values[:]:
            # eventually set in ProductSupplierInfoMapper
            # or ProductSupplierInfoLineMapper
            if item.get('__existing_odoo_id'):
                binding_id = item.pop('__existing_odoo_id')
                # update the record
                items.append((1, binding_id, item))
            else:
                # create the record
                items.append((0, 0, item))
        return items


class ProductSupplierInfoMapper(Component):
    _name = 'magento.product.supplierinfo.import.mapper'
    _inherit = 'magento.import.mapper'
    _apply_on = ['magento.product.supplierinfo']

    direct = [
        ('openerp_supplier_product_code', 'product_code'),
        ('openerp_supplier_product_name', 'product_name'),
        ('openerp_supplier_delay', 'delay'),
        ('openerp_supplier_price', 'price'),
        ('openerp_supplier_min', 'min_qty'),
        (external_to_m2o('openerp_supplier_name',
                         binding='magento.supplier'), 'name'),
    ]

    # TODO: to migrate later by configuring logistic routes
    # @mapping
    # def is_drop_shipping(self, record):
    #     """Check if the supplier support drop shipping in Magento
    #     and set direct_delivery_flag in OpenERP
    #     drop_shipping == 1 in Magento means
    #     direct_delivery_flag == True"""
    #     return {'direct_delivery_flag': (record.get('drop_shipping') == '1')}

    @mapping
    def from_magento(self, record):
        """ We don't keep a binding record, only use a flag.

        There is always 1 supplier on Magento, simply replaces the
        existing record, using this flag to differentiates it from the
        suppliers filed manually.
        """
        return {'from_magento': True}

    def finalize(self, map_record, values):
        values = super().finalize(map_record, values)
        mag_product_id = map_record.parent.source['product_id']
        binder = self.component(
            usage='magento.binder', model='magento.product.product')
        product = binder.to_internal(mag_product_id, unwrap=True)
        product_tmpl_id = product.product_tmpl_id.id
        if product_tmpl_id:
            # existing product, search for an existing supplier info
            # from Magento
            suppinfo = self.env['product.supplierinfo'].search(
                [
                    ('from_magento', '=', True),
                    ('product_id', '=', product_tmpl_id),
                ],
                limit=1)
            if not suppinfo:
                # from_magento has been introduced lately, try
                # to remap if the supplier is the same
                suppinfo = self.env['product.supplierinfo'].search(
                    [
                        ('name', '=', values['name']),  # means partner_id
                        ('product_id', '=', product_tmpl_id)
                    ],
                    limit=1,
                )

            if suppinfo:
                # supplier info already exists, keeps the id
                values['__existing_odoo_id'] = suppinfo.id
        return values


class DebonixProductImportMapper(Component):
    _inherit = 'magento.product.product.import.mapper'

    direct = [(source, target) for source, target in
              ProductImportMapper.direct if
              target not in ('standard_price', 'weight')] + \
             [('weight', 'weight_net')]

    @mapping
    def country(self, record):
        country_code = record.get('country_of_manufacture')
        if not country_code:
            return
        country = self.env['res.country'].search(
            [('code', '=', country_code)])
        if not country:
            raise MappingError('%s country code not found.' % country_code)
        return {'country_id': country[0].id}

    @mapping
    def brand(self, record):
        if not record.get('marque'):
            return
        binder = self.component(
            usage='magento.binder', model='magento.product.brand')
        brand = binder.to_internal(record['marque'], unwrap=True)
        return {'product_brand_id': brand.id}

    @mapping
    def universe(self, record):
        if not record.get('universe'):
            return {'magento_universe_id': False}
        binder = self.component(
            usage='magento.binder', model='magento.product.universe')
        universe = binder.to_internal(record['universe'])
        return {'magento_universe_id': universe.id}

    @mapping
    def cost(self, record):
        """Standard price is imported only if the inventory method is set on
        "standard".
        """
        # FIXME: is the 'cost' value always sent with 'openerp_cost_method'?
        if record.get('openerp_cost_method', '').lower() == 'standard':
            return {'standard_price': record.get('cost')}

    @mapping
    def intrastat(self, record):
        code = record.get('openerp_commodity')
        if not code:
            return
        code = code.strip()
        codes = self.env['report.intrastat.code'].search(
            [('intrastat_code', '=', code)])
        if codes:
            code_id = codes[0].id
        else:
            code_id = self.env['report.intrastat.code'].create(
                {'name': code, 'intrastat_code': code}).id
        return {'intrastat_id': code_id}

    @mapping
    def cost_method(self, record):
        method = record.get('openerp_cost_method')
        if not method:
            return
        return {'property_cost_method': method.lower()}

    @mapping
    def sale_ok(self, record):
        sale_ok = record.get('openerp_sale_ok') or 0
        return {'sale_ok': bool(int(sale_ok))}

    @mapping
    def purchase_ok(self, record):
        purchase_ok = record.get('openerp_purchase_ok') or 0
        return {'purchase_ok': bool(int(purchase_ok))}

    @mapping
    def state(self, record):
        state = record.get('openerp_state')
        if not state:
            return
        binder = self.component(
            usage='magento.binder', model='magento.product.state')
        state = binder.to_internal(state)
        return {'state': state}

    @mapping
    def uom(self, record):
        uom = record.get('openerp_supplier_product_unit')
        uom_id = None
        if uom:
            uoms = self.env['product.uom'].search(
                [('magento_name', '=', uom)])
            if uoms:
                uom_id = uoms[0].id
        if not uoms:
            # not found, fallback on default unit
            xmlid = ('product', 'product_uom_unit')
            try:
                __, uom_id = self.env['ir.model.data'].get_object_reference(
                    xmlid[0], xmlid[1])
            except ValueError:
                raise MappingError('Unit of measure with xmlid %s.%s is '
                                   'missing. Cannot create the orderpoint.' %
                                   (xmlid[0], xmlid[1]))

        return {'uom_id': uom_id, 'uom_po_id': uom_id}

    @mapping
    def conditionnement(self, record):
        """ This field is defined for certain PLN products, in order to
            factor into the quantity sold (ex: 1 unit of a 20m product will
            be set as '20'). The field can contain spaces, hence the replace()
        """
        conditionnement = record.get('conditionnement', False)
        if not conditionnement:
            return
        conditionnement = int(conditionnement.replace(' ', ''))
        if conditionnement:
            return {'magento_conditionnement': conditionnement}

    @only_create
    @mapping
    def orderpoint(self, record):
        xmlid = ('stock', 'warehouse0')
        try:
            warehouse = self.env['ir.model.data'].get_object(
                xmlid[0], xmlid[1])
        except ValueError:
            raise MappingError('Warehouse with xmlid %s.%s is missing. '
                               'Cannot create the orderpoint.' %
                               (xmlid[0], xmlid[1]))
        values = {
            'warehouse_id': warehouse.id,
            'product_uom': self.uom(record)['uom_id'],
            'location_id': warehouse.lot_stock_id.id,
            'product_min_qty': 0,
            'product_max_qty': 0,
            'qty_multiple': 1,
        }
        return {'orderpoint_ids': [(0, 0, values)]}

    @only_create
    @mapping
    def product_type(self, record):
        return {'type': 'product'}

    @mapping
    def odoo_id(self, record):
        """ Will bind the product on an existing product with the same sku,
        even if the product is already mapped with another product. In such
        situation, the magento.product.product binding will be reassigned
        to the product with the same SKU than the one on Magento.
        """
        product_model = self.env['product.product'].with_context(
            active_test=False)
        products = product_model.search(
            [('default_code', '=', record['sku'])])
        if products:
            return {'odoo_id': products[0].id}

    def finalize(self, map_record, values):
        values = super().finalize(map_record, values)
        record = map_record.source
        if not record['openerp_supplier_name']:
            return values
        supplier_record = dict((field, value) for field, value
                               in record.iteritems()
                               if field.startswith('openerp_supplier_') or
                               field == 'drop_shipping')
        map_child = self.component(
            usage='import.map.child', model='product.supplierinfo')
        items = map_child.get_items([supplier_record], map_record,
                                    'seller_ids',
                                    options=self.options)
        values['seller_ids'] = items
        return values


class DebonixCatalogImageImporter(Component):
    """ Do not import the images on the products """
    _inherit = 'magento.product.image.importer'

    def run(self, magento_id, binding_id):
        return
