# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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
import re
from suds.client import Client
from datetime import datetime
from openerp.osv import orm
from openerp.tools.translate import _

_compile_itemid = re.compile('[^0-9A-Za-z+\-_]')


class ColisPriveWebService(object):
    """ Connector with Colis Prive for labels using colisprive Web Services

    Allows to generate labels

    """

    def _add_security_header(self, client, carrier):
        # TODO comments
        username = carrier.ws_username
        password = carrier.ws_password
        auth = client.factory.create('AuthenticationHeader')
        auth.UserName = username
        auth.Password = password
        client.set_options(soapheaders=auth)

    def __init__(self, carrier):
        self.init_connection(carrier)

    def init_connection(self, carrier):
        # TODO comments
        try:
            self.client = Client(
                carrier.ws_url)
            self._add_security_header(self.client, carrier)
        except:
            raise orm.except_orm(
                _('Error'),
                _("There is an error with the web service url"))

    def _send_request(self, request, **kwargs):
        """ Wrapper for API requests

        :param request: callback for API request
        :param **kwargs: params forwarded to the callback

        """
        # TODO: Envoi mail si pas possible de se connecter au WS
        res = {}
        try:
            res['value'] = request(**kwargs)
            res['success'] = True
        except Exception as e:
            res['success'] = False
            res['errors'] = [e[0]]
        return res

    def _prepare_security(self, carrier):
        # TODO comments
        envelope = {
            'SecurityID':
                {'CPCustoID': carrier.ws_customer_id,
                 'AccountID': carrier.ws_account_id},
            'CltNum': carrier.ws_customer_id,
        }
        return envelope

    def _prepare_customer_info(self, picking):
        # TODO comments
        customer = picking.partner_id
        street1 = customer.street
        street2 = customer.street2
        zc = customer.zip
        city = customer.city
        country = customer.country_id and \
                  customer.country_id.name or ''
        DestName = customer.mag_chronorelais_code
        csgadd_info = {
            'DlvrName': customer.name,
            'DlvrAddress': {
                'Add1': street1,
                'Add2': street2 if street2 else '',
                'Add3': '',
                'Add4': '',
                'ZC': zc,
                'City': city,
                'Country': country
            },
            'DlvrEmail': customer.email if customer.email else '',
            'DlvrPhon': customer.phone if customer.phone else '',
            'DlvrGsm': customer.mobile if customer.mobile else '',
        }
        customer_info = {
            'CsgAdd': csgadd_info,
            'DestName': DestName,
        }
        return customer_info

    def _prepare_label_info(self, picking, carrier_file):
        # TODO comments
        if carrier_file:
            DestType = carrier_file.destype
            IsPclWithPOD = carrier_file.ispcl_withpod
        else:
            DestType = ''
            IsPclWithPOD = 0
        # Weight is in gram in the label so we convert it
        weight = int(picking.weight * 1000)
        label_info = {
            'OrderID': picking.name,
            'PclShipDate': datetime.today(),
            'PclWeight': weight,
            'IsPclWithPOD': IsPclWithPOD,
            'LabelFormat': 'PDF_ZEBRA',
            'DestType': DestType,
        }
        return label_info

    def _prepare_envelope(self, picking, carrier):
        # TODO comments
        envelope = self._prepare_security(carrier)
        envelope.update(self._prepare_customer_info(picking))
        envelope.update(self._prepare_label_info(picking, carrier.carrier_file_id))
        return envelope

    def _cancel_parcel(self, cpplcode, carrier):
        """
            Cancel the shipment if there is already a printed label
            for the picking
        """
        request = self.client.service.CancelParcel
        envelope = {'CPPclCode': cpplcode}
        envelope.update(self._prepare_security(carrier))
        if 'CltNum' in envelope:
            del envelope['CltNum']
        self._send_request(request, CancelParcelRequest=envelope)
        return True

    def generate_label(self, picking, carrier, cpplcode):
        """
        TODO : better comments
            Generate a label for a picking
        """
        envelope = self._prepare_envelope(picking, carrier)
        res = {'value': []}
        if cpplcode:
            self._cancel_parcel(cpplcode, carrier)
        request = self.client.service.SetParcel
        ws_response = self._send_request(request, SetParcelRequest=envelope)
        if not ws_response['success']:
            return ws_response
        response_value = ws_response['value']
        if response_value.WSResp.RtnCode == 0:
            res['value'] = {'carrier_code': response_value.CPPclCode,
                            'label_url': response_value.LabelUrl}
        else:
            res['errors'] = response_value.WSResp.RtnMessage.encode('utf-8')
        return res
