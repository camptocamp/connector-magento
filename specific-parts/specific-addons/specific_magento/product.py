# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012-2014 Camptocamp SA
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

import logging
from openerp.tools.translate import _
from openerp.osv import orm, fields
from openerp.addons.connector.unit.mapper import (
    backend_to_m2o,
    ExportMapper,
    ImportMapper,
    ImportMapChild,
    mapping,
    only_create,
)
from openerp.addons.connector.event import (on_record_write,
                                            on_record_create,
                                            )
from openerp.addons.connector.exception import MappingError
from openerp.addons.magentoerpconnect.unit.export_synchronizer import (
    export_record,
    MagentoExporter,
    )
from openerp.addons.magentoerpconnect.unit.import_synchronizer import (
    AddCheckpoint,
    )
from openerp.addons.magentoerpconnect.product import (
    ProductImport,
    ProductInventoryExport,
    ProductImportMapper,
    )
from .backend import magento_debonix
from .product_bundle import BoMBundleImporter


_logger = logging.getLogger(__name__)


class magento_product_product(orm.Model):
    _inherit = 'magento.product.product'
    _columns = {
        'magento_cost': fields.float('Computed Cost',
                                     help="Last computed cost to send "
                                          "on Magento."),
    }

    def product_type_get(self, cr, uid, context=None):
        selection = super(magento_product_product, self).product_type_get(
            cr, uid, context=context)
        if 'bundle' not in [item[0] for item in selection]:
            selection.append(('bundle', 'Bundle'))
        return selection

    def recompute_magento_cost(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]

        for product in self.read(cr, uid, ids, ['cost_price', 'magento_cost'],
                                 context=context):
            new_cost = product['cost_price']
            if new_cost != product['magento_cost']:
                self.write(cr, uid, product['id'],
                           {'magento_cost': new_cost},
                           context=context)
        return True


class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'
    _columns = {
        # indicates that the record has been created from Magento
        # using the `openerp_supplier_*` fields
        'from_magento': fields.boolean('From Magento', readonly=True),
    }


class pricelist_partnerinfo(orm.Model):
    _inherit = 'pricelist.partnerinfo'
    _columns = {
        # indicates that the record has been created from Magento
        # using the `openerp_supplier_*` fields
        'from_magento': fields.boolean('From Magento', readonly=True),
    }


@magento_debonix
class DebonixProductImport(ProductImport):
    _model_name = ['magento.product.product']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        super(DebonixProductImport, self)._import_dependencies()
        record = self.magento_record
        if record.get('marque'):
            self._import_dependency(record['marque'],
                                    'magento.product.brand')
        self._import_dependency(record['openerp_supplier_name'],
                                'magento.supplier')

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
            return _('The configurable product is not imported in OpenERP, '
                     'because only the simple products are used in the sales '
                     'orders.')
        return super(DebonixProductImport, self)._must_skip()


class CommonSupplierInfoMapChild(ImportMapChild):

    def format_items(self, items_values):
        items = []
        for item in items_values[:]:
            # eventually set in ProductSupplierInfoMapper
            # or ProductSupplierInfoLineMapper
            if item.get('__existing_openerp_id'):
                binding_id = item.pop('__existing_openerp_id')
                # update the record
                items.append((1, binding_id, item))
            else:
                # create the record
                items.append((0, 0, item))
        return items


@magento_debonix
class ProductSupplierInfoMapChild(CommonSupplierInfoMapChild):
    _model_name = 'product.supplierinfo'


@magento_debonix
class ProductSupplierInfoLineMapChild(CommonSupplierInfoMapChild):
    _model_name = 'pricelist.partnerinfo'


@magento_debonix
class ProductSupplierInfoLineMapper(ImportMapper):
    _model_name = 'pricelist.partnerinfo'

    direct = [('openerp_supplier_price', 'price'),
              ('openerp_supplier_min', 'min_quantity'),
              ]

    @mapping
    def from_magento(self, record):
        """ We don't keep a binding record, only use a flag.

        There is always 1 supplier on Magento, simply replaces the
        existing record, using this flag to differentiates it from the
        suppliers filed manually.
        """
        return {'from_magento': True}

    def finalize(self, map_record, values):
        values = super(ProductSupplierInfoLineMapper, self).finalize(
            map_record, values)
        suppinfo_id = self.options.suppinfo_id
        if not suppinfo_id:
            # new supplier
            return values

        line_ids = self.session.search(
            'pricelist.partnerinfo',
            [('from_magento', '=', True),
             ('suppinfo_id', '=', suppinfo_id)])
        if not line_ids:
            # from_magento has been introduced lately, try
            # to remap if the supplier is the same
            min_qty = map_record.source['openerp_supplier_min']
            line_ids = self.session.search(
                'pricelist.partnerinfo',
                [('suppinfo_id', '=', suppinfo_id),
                 ('min_quantity', '=', min_qty)])

        if line_ids:
            # supplier info line already exists, keeps the id
            values['__existing_openerp_id'] = line_ids[0]
        return values


@magento_debonix
class ProductSupplierInfoMapper(ImportMapper):
    _model_name = 'product.supplierinfo'

    direct = [('openerp_supplier_product_code', 'product_code'),
              ('openerp_supplier_product_name', 'product_name'),
              ('openerp_supplier_delay', 'delay'),
              (backend_to_m2o('openerp_supplier_name',
                              binding='magento.supplier'),
               'name'),
              ]

    @mapping
    def from_magento(self, record):
        """ We don't keep a binding record, only use a flag.

        There is always 1 supplier on Magento, simply replaces the
        existing record, using this flag to differentiates it from the
        suppliers filed manually.
        """
        return {'from_magento': True}

    def finalize(self, map_record, values):
        values = super(ProductSupplierInfoMapper, self).finalize(map_record,
                                                                 values)
        mag_product_id = map_record.parent.source['product_id']
        binder = self.get_binder_for_model('magento.product.product')
        product_id = binder.to_openerp(mag_product_id, unwrap=True)
        line_options = self.options.copy()
        for_create = True
        if product_id:
            # existing product, search for an existing supplier info
            # from Magento
            suppinfo_ids = self.session.search(
                'product.supplierinfo',
                [('from_magento', '=', True),
                 ('product_id', '=', product_id)])
            if not suppinfo_ids:
                # from_magento has been introduced lately, try
                # to remap if the supplier is the same
                suppinfo_ids = self.session.search(
                    'product.supplierinfo',
                    [('name', '=', values['name']),  # means partner_id
                     ('product_id', '=', product_id)])

            if suppinfo_ids:
                # supplier info already exists, keeps the id
                values['__existing_openerp_id'] = suppinfo_ids[0]
                line_options['suppinfo_id'] = suppinfo_ids[0]
                for_create = False

        if for_create:
            values['min_qty'] = 0.

        record = map_record.source
        price_record = {
            'openerp_supplier_price': record['openerp_supplier_price'],
            'openerp_supplier_min': record['openerp_supplier_min'],
        }
        map_child = self.get_connector_unit_for_model(
            self._map_child_class, 'pricelist.partnerinfo')
        items = map_child.get_items([price_record], map_record,
                                    'pricelist_ids',
                                    options=line_options)
        values['pricelist_ids'] = items
        return values


@magento_debonix
class DebonixProductImportMapper(ProductImportMapper):
    _model_name = 'magento.product.product'

    direct = ([(source, target) for source, target in
               ProductImportMapper.direct if
               not target == 'standard_price']
              )

    @mapping
    def country(self, record):
        country_code = record.get('country_of_manufacture')
        if not country_code:
            return
        s = self.session
        country_ids = s.search('res.country', [('code', '=', country_code)])
        if not country_ids:
            raise MappingError('%s country code not found.' % country_code)
        return {'country_id': country_ids[0]}

    @mapping
    def brand(self, record):
        if not record.get('marque'):
            return
        binder = self.get_binder_for_model('magento.product.brand')
        brand_id = binder.to_openerp(record['marque'], unwrap=True)
        return {'product_brand_id': brand_id}

    @mapping
    @only_create
    def cost(self, record):
        """ Standard price is only imported on creation,
        because it will be updated from OpenERP later.
        """
        return {'standard_price': record.get('cost')}

    @mapping
    def intrastat(self, record):
        s = self.session
        code = record.get('openerp_commodity')
        if not code:
            return
        code = code.strip()
        code_ids = s.search('report.intrastat.code',
                            [('intrastat_code', '=', code)])
        if code_ids:
            code_id = code_ids[0]
        else:
            code_id = s.create('report.intrastat.code',
                               {'name': code, 'intrastat_code': code})
        return {'intrastat_id': code_id}

    @mapping
    def cost_method(self, record):
        method = record.get('openerp_cost_method')
        if not method:
            return
        return {'cost_method': method.lower()}

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
        binder = self.get_binder_for_model('magento.product.state')
        state = binder.to_openerp(state)
        return {'state': state}

    @mapping
    def uom(self, record):
        uom = record.get('openerp_supplier_product_unit')
        uom_id = None
        if uom:
            uom_ids = self.session.search('product.uom',
                                          [('name', '=ilike', uom)])
            if uom_ids:
                uom_id = uom_ids[0]
        if not uom_id:
            # not found, fallback on default unit
            sess = self.session
            data_obj = sess.pool['ir.model.data']
            xmlid = ('product', 'product_uom_unit')
            try:
                __, uom_id = data_obj.get_object_reference(
                    sess.cr, sess.uid, xmlid[0], xmlid[1])
            except ValueError:
                raise MappingError('Unit of measure with xmlid %s.%s is '
                                   'missing. Cannot create the orderpoint.' %
                                   (xmlid[0], xmlid[1]))

        return {'uom_id': uom_id, 'uom_po_id': uom_id}

    @only_create
    @mapping
    def orderpoint(self, record):
        sess = self.session
        data_obj = sess.pool['ir.model.data']
        xmlid = ('stock', 'warehouse0')
        try:
            warehouse = data_obj.get_object(
                sess.cr, sess.uid, xmlid[0], xmlid[1], context=sess.context)
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
    def type(self, record):
        return {'type': 'product'}

    @only_create
    @mapping
    def openerp_id(self, record):
        """ Will bind the partner on an existing product with the same sku """
        sess = self.session
        with sess.change_context({'active_test': False}):
            product_ids = sess.search('product.product',
                                      [('default_code', '=', record['sku'])])
        if product_ids:
            return {'openerp_id': product_ids[0]}

    def finalize(self, map_record, values):
        values = super(DebonixProductImportMapper, self).finalize(map_record,
                                                                  values)
        record = map_record.source
        if not record['openerp_supplier_name']:
            return values
        supplier_record = dict((field, value) for field, value
                               in record.iteritems()
                               if field.startswith('openerp_supplier_'))
        map_child = self.get_connector_unit_for_model(
            self._map_child_class, 'product.supplierinfo')
        items = map_child.get_items([supplier_record], map_record,
                                    'seller_ids',
                                    options=self.options)
        values['seller_ids'] = items
        return values


@magento_debonix
class DebonixProductInventoryExport(ProductInventoryExport):
    _model_name = ['magento.product.product']

    def _get_data(self, product, fields):
        data = super(DebonixProductInventoryExport, self)._get_data(
            product, fields)

        if product.manage_stock:
            backorders = product.backorders
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


@magento_debonix
class DebonixProductExporter(MagentoExporter):
    """ Products are created on Magento. Export only changes of
    some fields.

    """
    _model_name = 'magento.product.product'


@magento_debonix
class DebonixProductExportMapper(ExportMapper):
    _model_name = 'magento.product.product'

    direct = [('magento_cost', 'cost'),
              ]


@magento_debonix
class DebonixAddCheckpoint(AddCheckpoint):
    _model_name = ['magento.product.product',
                   'magento.product.category',
                   ]

    def run(self, openerp_binding_id):
        # Deactivate the creation of checkpoint for products and categories
        # Debonix uses the 'state' of the products to know if it is ready
        # to sell
        pass


@on_record_create(model_names='magento.product.product')
@on_record_write(model_names='magento.product.product')
def delay_export(session, model_name, record_id, vals):
    if session.context.get('connector_no_export'):
        return
    if 'magento_cost' in vals:
        name = session.pool[model_name].name_get(
            session.cr, session.uid, record_id, session.context)[0][1]
        descr = "Export cost of product %s" % name
        export_record.delay(session, model_name,
                            record_id, fields=['magento_cost'],
                            description=descr)
