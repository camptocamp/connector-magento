# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Vincent Renaville. Copyright Camptocamp SA
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
###############################################################################

from openerp.osv import orm, fields
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.magentoerpconnect.product import export_product_inventory


class StockExportAllMagento(orm.TransientModel):
    _name = 'stock.export.all.magento'
    _description = 'Export Stock values for all products'

    _columns = {
                "check_confirm": fields.boolean('Confirm Export',
                help="""If the Confirm Export field is set to True,
                 Stock values for all products will be exported
                 to Magento."""),
    }

    def export_sock_all_product_magento(self, cr, uid, context=None):
        model_name = 'magento.product.product'
        magento_product_product_obj = self.pool.get(model_name)
        record_ids = magento_product_product_obj.search(cr,
                                                        uid,
                                                        [],
                                                        context=context)
        session = ConnectorSession(cr, uid, context=context)
        inventory_fields = ('manage_stock',
                            'backorders',
                            'magento_qty',
                            )
        for record_id in record_ids:
            export_product_inventory.delay(session, model_name,
                                       record_id, fields=inventory_fields,
                                       priority=30)

    def action_manual_export(self, cr, uid, ids, context=None):
        form = self.browse(cr, uid, ids[0], context=context)
        if form.check_confirm:
            ## We will export all datas
            self.export_sock_all_product_magento(cr, uid, context=context)
        return True
