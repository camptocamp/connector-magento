# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import xmlrpclib
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.addons.magentoerpconnect.backend import magento
from openerp.addons.magentoerpconnect.unit.backend_adapter import GenericAdapter
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.connector.event import on_record_create
from openerp.addons.connector.exception import IDMissingInBackend
from openerp.addons.magentoerpconnect.connector import get_environment
from openerp.addons.magentoerpconnect.related_action import unwrap_binding
import openerp.addons.decimal_precision as dp


class magento_credit_memo(orm.Model):
    """ Binding Model for the Magento Credit Memo """
    _name = 'magento.credit.memo'
    _inherit = 'magento.binding'
    _inherits = {'account.invoice': 'openerp_id'}
    _description = 'Magento Credit Meno'

    _columns = {
        'openerp_id': fields.many2one(
            'account.invoice',
            string='Invoice',
            required=True,
            ondelete='cascade'),
        'magento_order_id': fields.many2one(
            'magento.sale.order',
            string='Magento Sale Order',
            ondelete='set null'),
        'magento_credit_amount': fields.float(
            'Magento credit amount',
            digits_compute=dp.get_precision('Account')),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'An credit memo with the same ID on Magento already exists.'),
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         'A Magento credit memo binding for this invoice already exists.'),
    ]


class account_invoice(orm.Model):
    """ Adds the ``one2many`` relation to the Magento bindings
    (``magento_credit_memo_ids``)"""
    _inherit = 'account.invoice'

    _columns = {
        'magento_credit_memo_ids': fields.one2many(
            'magento.credit.memo', 'openerp_id',
            string="Magento Credit Memo Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['magento_credit_memo_ids'] = False
        return super(account_invoice, self).copy_data(cr, uid, id,
                                                      default=default,
                                                      context=context)

    def _create_credit_memo(self, cr, uid, refund, amount, context=None):
        """
        Create a ``magento.credit.memo`` record. This record will then
        be exported to Magento.
        """
        if not refund.claim_id:
            raise
        invoice = refund.claim_id.invoice_id
        # find the magento store to retrieve the backend
        # we use the shop as many sale orders can be related to an invoice
        for sale in invoice.sale_ids:
            for magento_sale in sale.magento_bind_ids:
                binding_exists = False
                for mag_inv in refund.magento_credit_memo_ids:
                    if mag_inv.backend_id.id == magento_sale.backend_id.id:
                        binding_exists = True
                        break
                if binding_exists:
                    continue
                self.pool['magento.credit.memo'].create(
                    cr, uid, {'backend_id': magento_sale.backend_id.id,
                              'openerp_id': refund.id,
                              'magento_order_id': magento_sale.id,
                              'magento_credit_amount': amount},
                    context=context)

    def _search_available_refund(self, cr, uid, partner_id, context=None):
        if context is None:
            context = {}
        if context.get('manual_credit_line'):
            return  self.search(
                cr, uid, [('type', '=', 'out_refund'),
                          ('state', '!=', 'cancel'),
                          ('credit_note_amount', '!=', 0),
                          ('magento_credit_memo_ids', '=', False),
                          '|', ('partner_id', '=', partner_id),
                          ('partner_id', 'child_of', partner_id)],
                order="date_invoice",
                context=context)
        return super(account_invoice, self)._search_available_refund(
            cr, uid, partner_id, context=context)


@magento
class CreditMemoAdapter(GenericAdapter):
    """ Backend Adapter for the Magento Credit Memo """
    _model_name = 'magento.credit.memo'
    _magento_model = 'sales_order_creditmemo'
#    _admin_path = 'sales_invoice/view/invoice_id/{id}'

    def _call(self, method, arguments):
        try:
            return super(CreditMemoAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Magento API
            # when the credit memo does not exist
            if err.faultCode == 100:
                raise IDMissingInBackend
            else:
                raise

    def create(self, order_increment_id, items, comment, email,
               include_comment, credit_amount):
        """ Create a record on the external system """
        return self._call('%s.create' % self._magento_model,
                          [order_increment_id, items, comment,
                           email, include_comment, credit_amount])

    def search_read(self, filters=None, order_id=None):
        """ Search records according to some criterias
        and returns their information

        :param order_id: 'order_id' field of the magento sale order, this
                         is not the same field than 'increment_id'
        """
        if filters is None:
            filters = {}
        if order_id is not None:
            filters['order_id'] = {'eq': order_id}
        return super(CreditMemoAdapter, self).search_read(filters=filters)


@magento
class CreditMemoSynchronizer(ExportSynchronizer):
    """ Export credit memo to Magento """
    _model_name = ['magento.credit.memo']

    def _export_refund(
            self, magento_id, lines_info, mail_notification, credit_amount):
        if not lines_info:  # invoice without any line for the sale order
            return
        return self.backend_adapter.create(magento_id,
                                           lines_info,
                                           _("Refund Created"),
                                           mail_notification,
                                           False,
                                           credit_amount)

    def _get_lines_info(self, refund):
        """
        Get the line to export to Magento. In case some lines doesn't have a
        matching on Magento, we ignore them. This allow to add lines manually.

        :param refund: refund is an magento.credit.memo record
        :type refund: browse_record
        :return: dict of {magento_order_line_id: quantity}
        :rtype: dict
        """
        item_qty = {}
        # get product and quantities to invoice
        # if no magento id found, do not export it
        order = refund.magento_order_id
        for line in refund.invoice_line:
            product = line.product_id
            # find the order line with the same product
            # and get the magento item_id (id of the line)
            # to invoice
            order_line = next((line for line in order.magento_order_line_ids
                               if line.product_id.id == product.id),
                              None)
            if order_line is None:
                continue

            item_id = order_line.magento_id
            item_qty.setdefault(item_id, 0)
            item_qty[item_id] += line.quantity
        return item_qty

    def run(self, binding_id):
        """ Run the job to export the refund """
        sess = self.session
        refund = sess.browse(self.model._name, binding_id)

        magento_order = refund.magento_order_id
        magento_stores = magento_order.shop_id.magento_bind_ids
        magento_store = next((store for store in magento_stores
                              if store.backend_id.id == refund.backend_id.id),
                             None)
        assert magento_store
        mail_notification = False #TODO !
        credit_amount = refund.magento_credit_amount
        lines_info = self._get_lines_info(refund)
        creditmemodata = {'qtys': lines_info}
#TODO shipping amount
        magento_id = None
        try:
            magento_id = self._export_refund(magento_order.magento_id,
                                             creditmemodata,
                                             mail_notification,
                                             credit_amount)
        except xmlrpclib.Fault as err:
            raise #TODO
#        if not magento_id:
#            # If Magento returned no ID, try to find the Magento
#            # invoice, but if we don't find it, let consider the job
#            # as done, because Magento did not raised an error
#            magento_id = self._get_existing_invoice(magento_order)
#
        if magento_id:
            self.binder.bind(magento_id, binding_id)
#
#    def _get_existing_invoice(self, magento_order):
#        invoices = self.backend_adapter.search_read(
#            order_id=magento_order.magento_order_id)
#        if not invoices:
#            return
#        if len(invoices) > 1:
#            return
#        return invoices[0]['increment_id']


@on_record_create(model_names='magento.credit.memo')
def delay_export_credit_memo(session, model_name, record_id, vals):
    """
    Delay the job to export the magento credit memo.
    """
    export_refund.delay(session, model_name, record_id)


@job
@related_action(action=unwrap_binding)
def export_refund(session, model_name, record_id):
    """ Export a validated refund. """
    invoice = session.browse(model_name, record_id)
    backend_id = invoice.backend_id.id
    env = get_environment(session, model_name, backend_id)
    refund_exporter = env.get_connector_unit(CreditMemoSynchronizer)
    return refund_exporter.run(record_id)
