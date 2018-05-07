# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Charbel Jacquin (Camptocamp)
#    Copyright 2015 Camptocamp SA
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
from openerp.osv import osv, fields
from openerp.exceptions import Warning
from datetime import datetime

from StringIO import StringIO
import ftplib
import os
import logging
import socket
from tools import handlebars
import re

_logger = logging.getLogger('EDIFACT')
_logger.setLevel(logging.DEBUG)


class purchase_order(osv.Model):
    """ extends purchase.order to implement edifact message generation """
    _inherit = "purchase.order"

    _columns = {
        'edifact_sent': fields.boolean('EDI Sent', readonly=True),
        'edifact_removed':  fields.boolean('EDI Removed', readonly=True)
    }

    _defaults = {
        'edifact_sent': False,
        'edifact_removed': False,
    }

    _edi_template = None

    def wkf_approve_order(self, cr, uid, ids, context=None):

        _logger.debug("wkf_approve_order, calling super")
        super(purchase_order, self).wkf_approve_order(
            cr, uid, ids, context=context)
        _logger.debug("wkf_approve_order, calling generate_edifact() "
                      "if supplier is SOGEDESCA and customer address "
                      "is present (indicates drop-shipping).")
        for order in self.browse(cr, uid, ids, context=context):
            if order.dest_address_id and order.partner_id.edifact_message:
                self.generate_edifact(cr, uid, ids, context)

    def check_removed_edifact_files(self, cr, uid, ids=None, context=None):
        """ Check for edifact files removed from the ftp server

        This method will be called in a cron job.
        """
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        host = company.edifact_host
        ftpuser = company.edifact_user
        ftppass = company.edifact_password
        droppath = company.edifact_purchase_path

        ids = self.search(cr, uid, ['&', ('edifact_sent', '=', True),
                                    ('edifact_removed', '=', False)],
                          context=context)

        to_check = self.read(cr, uid, ids, ['name'], context=context)
        removed = []

        if not host:
            # assuming local path
            for rec in to_check:
                fullpath = os.path.join(droppath, '%s.edi' % rec['name'])
                if not os.path.exists(fullpath):
                    removed.append(rec['id'])
        else:
            ftp = None
            try:
                ftp = ftplib.FTP(host, ftpuser, ftppass)
                ftp.cwd(droppath)
                # doing it by ftp
                listing = ftp.nlst()
                for rec in to_check:
                    filename = '%s.edi' % rec['name']
                    if filename not in listing:
                        removed.append(rec['id'])
            except (socket.error, IOError) as err:
                raise Warning("Could not check processed purchase order "
                              "EDIFACT messages on FTP server: %s"
                              % err.message)
            finally:
                # Test for variable, None if connection failed
                if ftp:
                    ftp.quit()

        if removed:
            self.write(cr, uid, removed,
                       {'edifact_removed': True}, context=context)
        return True

    def generate_edifact(self, cr, uid, ids, context=None):
        """ generate EDIFACT message for the selected purchase orders """
        assert len(ids) == 1   # FIXME For now one, we will do batch later

        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            _logger.debug('ORDER: %s', order.name)

        if order.edifact_sent:
            raise Warning("EDIFACT document already sent to partner. "
                          "If you need to regenerate, please ask your "
                          "DBA to clear the 'edifact_sent' status on %s" %
                          order.name)

        mapping = self._build_mapping(order)
        template = self._get_template()
        renderer = make_render_engine()

        message = renderer.render(template, mapping)

        _logger.debug('message for %r:\n%r', order.name, message)

        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        host = company.edifact_host
        ftpuser = company.edifact_user
        ftppass = company.edifact_password
        droppath = company.edifact_purchase_path

        filename = '%s.edi' % order.name
        fullpath = os.path.join(droppath, filename)

        try:
            message = message.encode('latin1')
        except UnicodeEncodeError:
            _logger.warn("EDIFACT message contains non latin1 encodable "
                         "unicode caracters, they have been replaced by '?'")
            message = message.encode('latin1', 'replace')

        if not host:
            if not os.path.exists(droppath):
                os.mkdir(droppath)
            self._save_edi(fullpath, message)
        else:
            ftp = None
            try:
                ftp = ftplib.FTP(host, ftpuser, ftppass)
                try:
                    ftp.cwd(droppath)
                except IOError as err:
                    raise Warning('could not cd to %r on ftp server: %s' %
                                  (droppath, err.message))
                content = StringIO(message)
                ftp.storlines('STOR ' + filename, content)
            except socket.error as err:
                raise Warning("could not save EDIFACT message "
                              "on FTP server: %s" %
                              err.message)
            finally:
                # Test for variable, None if connection failed
                if ftp:
                    ftp.quit()

        # order.edifact_sent = True
        vals = {'edifact_sent': True}
        self.write(cr, uid, [order.id], vals, context=context)
        return True

    def _build_mapping(self, order):
        """ generate data mapping needed for template rendering """

        supplier = order.partner_id
        invoice_address = order.sale_id \
            and order.sale_id.partner_invoice_id \
            or order.dest_address_id
        shipping_address = order.dest_address_id

        mapping = {
            'codefiliale': supplier and supplier.code_filiale or '',
            'siretFiliale': supplier and supplier.siret_filiale or '',
            'dateCmd': datetime.now().strftime('%Y%m%d'),
            'heureCmd': datetime.now().strftime('%H%M%S'),
            'codeAgence': supplier and supplier.code_agence or '',
            'siretAgence': supplier and supplier.siret_agence or '',
            'siretDebonix': '49039922700035',
            'noCmd': order and order.name or '',
            'refCmd': order and order.name or '',
            'dateLiv': order
            and order.minimum_planned_date
            and order.minimum_planned_date.replace('-', '')
            or '',
            'compteDebonix': supplier and supplier.compte_debonix or '',
            'invoiceAddr1': invoice_address
            and invoice_address.name
            and invoice_address.name[:35]
            or '',
            'invoiceAddr2': invoice_address
            and invoice_address.name
            and invoice_address.name[35:70]
            or '',
            'invoiceAddr3': invoice_address
            and invoice_address.street
            and invoice_address.street[:35]
            or '',
            'invoiceAddr4': invoice_address
            and invoice_address.street
            and invoice_address.street[35:70]
            or '',
            'invoiceAddr5': invoice_address
            and invoice_address.street2
            and invoice_address.street2[:35]
            or '',
            'invoiceZipCode': invoice_address and invoice_address.zip or '',
            'invoiceCity': invoice_address and invoice_address.city or '',
            'invoiceCountryCode': invoice_address
            and invoice_address.country_id
            and invoice_address.country_id.code or '',
            'invoiceTel': invoice_address and invoice_address.phone or '',
            'invoiceFax': invoice_address and invoice_address.fax or '',
            'commentaire': invoice_address and invoice_address.email or '',
            'totalHT': int(order.amount_untaxed * 1000),
            'totalTVA': int(order.amount_tax * 1000),
            'totalTTC': int(order.amount_total * 1000)
        }

        if shipping_address.mag_chronorelais_company:
            mapping.update({
                'shippingAddr1': shipping_address
                and shipping_address.name
                and shipping_address.name[:35]
                or '',
                'shippingAddr2': shipping_address
                and shipping_address.mag_chronorelais_company
                and shipping_address.mag_chronorelais_company[:35]
                or '',
                'shippingAddr3': shipping_address
                and shipping_address.street
                and shipping_address.street[:35]
                or '',
                'shippingAddr4': shipping_address
                and shipping_address.street
                and shipping_address.street[35:70]
                or '',
                'shippingAddr5': shipping_address
                and shipping_address.street2
                and shipping_address.street2[:35]
                or '',
                'shippingZipCode': shipping_address
                and shipping_address.zip
                or '',
                'shippingCity': shipping_address
                and shipping_address.city
                or '',
                'shippingCountryCode': shipping_address
                and shipping_address.country_id
                and shipping_address.country_id.code or '',
                'shippingTel': shipping_address
                and shipping_address.phone
                or '',
                'shippingFax': shipping_address
                and shipping_address.fax
                or '',
                'codeServiceVendeur': shipping_address
                and shipping_address.mag_chronorelais_code
                or ''
            })
        else:
            mapping.update({
                'shippingAddr1': shipping_address
                and shipping_address.name
                and shipping_address.name[:35]
                or '',
                'shippingAddr2': shipping_address
                and shipping_address.name
                and shipping_address.name[35:70]
                or '',
                'shippingAddr3': shipping_address
                and shipping_address.street
                and shipping_address.street[:35]
                or '',
                'shippingAddr4': shipping_address
                and shipping_address.street
                and shipping_address.street[35:70]
                or '',
                'shippingAddr5': shipping_address
                and shipping_address.street2
                and shipping_address.street2[:35]
                or '',
                'shippingZipCode': shipping_address
                and shipping_address.zip
                or '',
                'shippingCity': shipping_address
                and shipping_address.city
                or '',
                'shippingCountryCode': shipping_address
                and shipping_address.country_id
                and shipping_address.country_id.code or '',
                'shippingTel': shipping_address
                and shipping_address.phone
                or '',
                'shippingFax': shipping_address
                and shipping_address.fax
                or '',
                'codeServiceVendeur': ''
            })
        lines = []
        if order.sale_id and order.sale_id.carrier_id \
                and order.sale_id.carrier_id.origin_edi_code:
            # We will get codeOrigine occording to value inside reference
            mapping.update({'codeOrigine':
                            order.sale_id.carrier_id.origin_edi_code})
        else:
            mapping.update({'codeOrigine': 'DB'})
        total_qty = 0
        for line_index, order_line in enumerate(order.order_line):
            product = order_line.product_id
            uom = product.uom_id
            supplier_product_code = product.seller_ids\
                and product.seller_ids[0]\
                and product.seller_ids[0].product_code\
                and product.seller_ids[0].product_code[:9]\
                or product.code[:9]
            quantity = int(order_line.product_qty * 1000)
            if product.magento_conditionnement:
                quantity *= product.magento_conditionnement
            line = {
                'codag': supplier_product_code,
                'libelle': product
                and product.name
                and product.name[:70]
                or '',
                'prixUnitaireNet': int(order_line.price_unit * 10000),
                'qte': quantity,
                'refarticleFournisseur': product and product.code or '',
                'ligne': line_index+1,
                'montantLigne': int(order_line.price_subtotal * 1000),
                'uq': uom.edi_code and uom.edi_code or 'P',
                'dateLiv': order_line
                and order_line.date_planned
                and order_line.date_planned.replace('-', '')
                or '',
                'uep': 1    # CHECKME,
            }

            total_qty += line['qte']
            lines.append(line)

        mapping['__lines__'] = lines
        mapping['totalQte'] = total_qty
        mapping['totalLigne'] = line_index+1
        _logger.debug('DATA extracted [%d] lines', len(lines))

        return mapping

    @classmethod
    def _get_template(cls):
        """ get EDIFACT template for purchase orders """
        if cls._edi_template is None:
            module_path = os.path.dirname(os.path.abspath(__file__))
            specfile = os.path.join(module_path, 'debonix.mustache')
            with open(specfile) as data:
                cls._edi_template = data.read()
        return cls._edi_template

    @staticmethod
    def _save_edi(path, message):
        """ save EDIFACT message """
        if os.path.exists(path):
            raise Warning("""EDIFACT file %s already exists.
            Please remove it before you can regenerate""" % path)

        with open(path, 'w') as out:
            out.write(message)

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'edifact_sent': False,
            'edifact_removed': False,
        })
        return super(purchase_order, self).copy(cr, uid, id, default,
                                                context=context)


class purchase_order_cancel_edi(osv.TransientModel):

    _name = 'purchase.order.edi.cancel'
    _description = 'Purchase Order EDI Cancel'
    _inherit = ['mail.thread']

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        edifact_regex_ref = company.edifact_regex_ref
        edifact_regex_errors = company.edifact_regex_errors
        purchase_order_obj = self.pool['purchase.order']
        picking_in_obj = self.pool['stock.picking.in']
        # Call Regex
        pattern_ref = re.compile(edifact_regex_ref, re.MULTILINE | re.UNICODE)
        pattern_errors = re.compile(edifact_regex_errors,
                                    re.MULTILINE | re.UNICODE)
        ref = re.search(pattern_ref, msg['body'])
        errors = re.findall(pattern_errors, msg['body'])
        if ref:
            purchase_ids = purchase_order_obj.search(cr, uid,
                                                     [('name', '=',
                                                       ref.group(1))],
                                                     context=context)
            purchase_list = purchase_order_obj.browse(cr, uid,
                                                      purchase_ids,
                                                      context=context)
            for purchase_order in purchase_list:
                # We search packing for this purchase
                if purchase_order.picking_ids and \
                        purchase_order.state == 'approved':
                    picking_ids = [picking.id for picking
                                   in purchase_order.picking_ids]
                    picking_in_obj.action_cancel(cr, uid,
                                                 picking_ids, context=context)
                    # We will set the current purchase order edifact to false
                    purchase_order_obj.write(cr, uid,
                                             [purchase_order.id],
                                             {'edifact_sent': False,
                                              'edifact_removed': False},
                                             context=context)
                    message = "There was an error(s) in EDI File  : %s" \
                        % "\n".join(errors)
                    purchase_order_obj.message_post(cr, uid, purchase_order.id,
                                                    body=message,
                                                    context=context)


def make_render_engine():
    renderer = handlebars.Renderer(escape=lambda u: u)

    def lj(v, width, fill=' '):
        v = unicode(v)
        return v.ljust(width, fill)

    def rj(v, width, fill=' '):
        v = unicode(v)
        return v.rjust(width, fill)

    renderer.register_helper('lj', lj)
    renderer.register_helper('rj', rj)

    return renderer
