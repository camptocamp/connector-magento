# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich (Camptocamp)
#    Copyright 2017 Camptocamp SA
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
from openerp.osv import orm
import xml.etree.ElementTree as ET


class PurchaseOrder(orm.Model):
    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        result = super(PurchaseOrder, self).wkf_confirm_order(cr, uid, ids,
                                                              context=context)
        self.action_toolstream_emails(cr, uid, ids, context=context)
        return result

    def action_toolstream_emails(self, cr, uid, ids, context=None):
        toolstream_supplier_ids = self.pool['res.partner'].search(cr, uid,
            [('name', '=', 'TOOLSTREAM'), ('supplier', '=', True)],
            context=context)
        for purchase in self.browse(cr, uid, ids, context=context):
            if purchase.partner_id.id in toolstream_supplier_ids:
                self._send_toolstream_email(cr, uid, purchase, context=context)
        return True

    def _send_toolstream_email(self, cr, uid, purchase, context=None):
        # Create XML message for Toolstream and send it by e-mail
        order = ET.Element('order')
        message = ET.SubElement(order, 'message', {'type': 'order'})
        head = ET.SubElement(message, 'head', {'type': 'order'})
        doc = ET.SubElement(head, 'doc', {'type': 'sales-order'})
        number = ET.SubElement(doc, 'number')
        number.text = purchase.name
        cust_order_reference = ET.SubElement(head, 'reference',
                                             {'type': 'cust-order-no'})
        cust_order_reference.text = purchase.name
        anal_reference = ET.SubElement(head, 'reference', {'type': 'anal-3'})
        anal_reference.text = 'EDI'
        address = ET.SubElement(head, 'address', {'type': 'delivery'})
        address_reference = ET.SubElement(address, 'reference')
        address_reference.text = '00004664'
        line_count = 1
        for order_line in purchase.order_line:
            product = order_line.product_id
            supplier_info = product.seller_ids and product.seller_ids[0]
            if not supplier_info:
                continue
            line = ET.SubElement(message, 'line', {'id': str(line_count)})
            line_count += 1
            item = ET.SubElement(line, 'item', {'type': 'product'})
            item.text = supplier_info.product_code
            quantity = ET.SubElement(line, 'quantity', {'type': 'ordered'})
            quantity.text = str(int(order_line.product_qty))

        # Set DELIVERYZONEFREE or DELIVERYZONEA depending on order total
        delivery_line = ET.SubElement(message, 'line', {'id': '999'})
        delivery_item = ET.SubElement(delivery_line, 'item',
                                      {'type': 'service'})
        if purchase.free_postage_reached:
            delivery_item.text = 'DELIVERYZONEFREE'
        else:
            delivery_item.text = 'DELIVERYZONEA'
        delivery_quantity = ET.SubElement(delivery_line, 'quantity',
                                          {'type': 'ordered'})
        delivery_quantity.text = '1'
        message = ET.tostring(order, encoding="utf-8")

        # Send message to Toolstream
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        if company.toolstream_email_address:
            attachment_obj = self.pool['ir.attachment']
            mail_obj = self.pool['mail.mail']
            filename = purchase.name + ".sor"
            toolstream_account_id = '00004664-b2967762e7708e2ff3ba1c7b6d5212'
            attachment_id = attachment_obj.create(
                cr, uid,
                {'datas': message.encode('base64'),
                 'name': filename,
                 'datas_fname': filename},
                context=context)
            message_id = mail_obj.create(
                cr, uid,  {'subject': toolstream_account_id,
                           'email_to': company.toolstream_email_address,
                           'attachment_ids': [(6, 0, [attachment_id])]},
                context=context)
            mail_obj.send(cr, uid, [message_id], context=context)
