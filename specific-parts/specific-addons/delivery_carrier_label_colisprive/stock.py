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
import urllib2


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _send_mail_label_errors(self, cr, uid, claim_id, context=None):
        # TODO comments
        data_obj = self.pool['ir.model.data']
        email_obj = self.pool['email.template']
        __, template_id = data_obj.get_object_reference(
            cr, uid, 'delivery_carrier_label_colisprive',
            'web_service_error_template_mail')
        email_obj.send_mail(cr, uid, template_id, claim_id, context=context)
        return True

    def _create_claim_errors(self, cr, uid, picking, errors, context=None):
        # TODO comments
        __, categ_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'debonix_purchase_edi', 'categ_claim_pln_incident')
        description = _("There is an error with the Web service for the "
                        "picking %s: %s")%(picking.name, errors.decode('utf-8'))
        name = _('WS error with %s')%(picking.name)
        claim_vals = {'name': name,
                      'description': description,
                      'categ_id': categ_id,
                      'claim_type': 'other'}
        claim_id = self.pool['crm.claim'].create(cr, uid, claim_vals,
                                                 context=context)
        return claim_id

    def _manage_label_errors(self, cr, uid, picking, errors, context=None):
        # TODO comments
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

    def _generate_colisprive_label(self, cr, uid, pick,
                                      tracking_ids=None, context=None):
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
            self._manage_label_errors(cr, uid, picking,
                                      res['errors'], context=context)
            return label
        # Write tracking_number on picking
        gen_label = res['value']
        tracking_number = gen_label['carrier_code']
        self.write(cr, uid, picking.id,
                   {'carrier_tracking_ref': tracking_number},
                   context=context)
        if gen_label.get('label_url'):
            filename = tracking_number + '.' + 'pdf'
            data_file = self.recup_label_data_file(gen_label['label_url'])
            label = {'file': data_file,
                     'file_type': 'pdf',
                      'name': filename,
                      }
        return [label]

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
            return self._generate_colisprive_label(
                cr, uid, picking,
                tracking_ids=tracking_ids,
                context=context)
        return super(stock_picking, self).\
            generate_shipping_labels(cr, uid, ids, tracking_ids=tracking_ids,
                                     context=context)