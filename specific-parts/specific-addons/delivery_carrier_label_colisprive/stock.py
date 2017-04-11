# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Charline Dumontet
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
from openerp.osv import orm, fields
from openerp.tools.translate import _
from colisprive.web_service import ColisPriveWebService
import openerp.pooler as pooler
import urllib2
from openerp.exceptions import Warning


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'colisprive_label_url': fields.char('Created label', size=128),
    }

    def _send_mail_label_errors(self, cr, uid, claim_id, context=None):
        """
            Send a mail if there is an error with the label
        """
        data_obj = self.pool['ir.model.data']
        email_obj = self.pool['email.template']
        __, template_id = data_obj.get_object_reference(
            cr, uid, 'delivery_carrier_label_colisprive',
            'web_service_error_template_mail')
        email_obj.send_mail(cr, uid, template_id, claim_id, context=context)
        return True

    def _create_claim_errors(self, cr, uid, picking, errors, context=None):
        """
            Create a claim if there is an error with the label
        """
        __, categ_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'delivery_carrier_label_colisprive',
            'categ_claim_colisprive_incident')
        description = _("There is an error with the Web service for the "
                        "picking %s: %s") % (picking.name, errors)
        name = _('WS error with %s') % (picking.name)
        claim_vals = {'name': name,
                      'description': description,
                      'categ_id': categ_id,
                      'claim_type': 'other'}
        claim_id = self.pool['crm.claim'].create(cr, uid, claim_vals,
                                                 context=context)
        return claim_id

    def _manage_label_errors(self, cr, uid, picking, errors, context=None):
        claim_id = self._create_claim_errors(cr, uid, picking, errors,
                                             context=context)
        if claim_id:
            self._send_mail_label_errors(cr, uid, claim_id, context=context)
        return True

    def recup_label_data_file(self, url_file):
        """
            Open, read and return the binary data of the PDF
        """
        open_file = urllib2.urlopen(url_file)
        data_file = open_file.read()
        return data_file

    def generate_carrier_files(self, cr, uid, ids, auto=True,
                               recreate=False, context=None):
        """
            Replace base method to check if there is edifact sent
        """
        carrier_file_obj = self.pool.get('delivery.carrier.file')
        carrier_file_ids = {}
        for picking in self.browse(cr, uid, ids, context):
            # Check the edifact_sent of the purchase
            purchase_edi = False
            sale_id = picking.sale_id and picking.sale_id.id or False
            if sale_id:
                purchase_obj = self.pool['purchase.order']
                purchase_order_ids = purchase_obj.search(
                    cr, uid, [('sale_id', '=', sale_id)], context=context)
                for purchase in purchase_obj.browse(
                        cr, uid,purchase_order_ids, context=context):
                    if purchase.edifact_sent:
                        purchase_edi = True
                        break
            if purchase_edi:
                continue
            if picking.type != 'out':
                continue
            if not recreate and picking.carrier_file_generated:
                continue
            carrier = picking.carrier_id
            if not carrier or not carrier.carrier_file_id:
                continue
            if auto and not carrier.carrier_file_id.auto_export:
                continue
            p_carrier_file_id = picking.carrier_id.carrier_file_id.id
            carrier_file_ids.setdefault(p_carrier_file_id, []).\
                append(picking.id)

        for carrier_file_id, carrier_picking_ids\
                in carrier_file_ids.iteritems():
            carrier_file_obj.generate_files(cr, uid, carrier_file_id,
                                            carrier_picking_ids,
                                            context=context)
        return True

    def _generate_colisprive_label(self, cr, uid, pick, tracking_ids=None,
                                   context=None):
        """
            Generate labels and write tracking numbers received
        """
        if isinstance(pick, int):
            picking = self.browse(cr, uid, pick, context=context)
        elif isinstance(pick, list):
            picking = self.browse(cr, uid, pick[0], context=context)
        else:
            picking = pick
        label = []
        carrier = picking.carrier_id
        cpplcode = picking.carrier_tracking_ref
        webservice_class = ColisPriveWebService
        web_service = webservice_class(carrier)
        res = web_service.generate_label(picking, carrier, cpplcode)
        if 'errors' in res:
            # We used a new cr to create a mail and a claim but send a raise
            # to the delivery
            errors = res['errors'].decode('utf-8')
            new_cr = pooler.get_db(cr.dbname).cursor()
            self._manage_label_errors(new_cr, uid, picking,
                                      errors, context=context)
            new_cr.commit()
            new_cr.close()
            error_msg = _("Impossible delivery: There is an error with the "
                          "Web service '%s'. Please contact your "
                          "administrator") % (errors)
            raise Warning(error_msg)
        # Write tracking_number on picking
        gen_label = res['value']
        tracking_number = gen_label['carrier_code']
        self.write(cr, uid, picking.id,
                   {'carrier_tracking_ref': tracking_number},
                   context=context)
        label_url = gen_label.get('label_url', '')
        if label_url:
            picking.write({'colisprive_label_url': label_url})
            filename = tracking_number + '.' + 'pdf'
            data_file = self.recup_label_data_file(gen_label['label_url'])
            label = {'file': data_file,
                     'file_type': 'pdf',
                     'name': filename,
                     }
        return [label], label_url

    def generate_shipping_labels(self, cr, uid, ids, tracking_ids=None,
                                 context=None):
        """
            Label generation for Colisprive
        """
        if isinstance(ids, (long, int)):
            ids = [ids]
        assert len(ids) == 1
        picking = self.browse(cr, uid, ids[0], context=context)
        if picking.carrier_id.type == 'colisprive':
            label, label_url = self._generate_colisprive_label(
                cr, uid, picking,
                tracking_ids=tracking_ids,
                context=context)
            return label
        return super(stock_picking, self).\
            generate_shipping_labels(cr, uid, ids, tracking_ids=tracking_ids,
                                     context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'colisprive_label_url': ''})
        return super(stock_picking, self).copy(cr, uid, id, default=default,
                                               context=context)


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    _columns = {
        'colisprive_label_url': fields.char('Created label', size=128),
    }
