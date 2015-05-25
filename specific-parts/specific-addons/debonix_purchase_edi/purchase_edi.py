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

from StringIO import StringIO
import os
import paramiko
import logging
import socket
from tools import handlebars

_logger = logging.getLogger('EDIFACT')
_logger.setLevel(logging.DEBUG)


class purchase_order(osv.Model):
    """ extends purchase.order to implement edifact message generation """
    _inherit = "purchase.order"

    _columns = {
        'create_date': fields.datetime('Creation Time', readonly=True),
        'edifact_sent': fields.boolean('EDI Sent', readonly=True),
        'edifact_removed':  fields.boolean('EDI Removed', readonly=True)
    }

    _edi_template = None

    def wkf_confirm_order(self, cr, uid, ids, context=None):

        _logger.info("wkf_confirm_order, calling super")
        super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
        _logger.info("wkf_confirm_order, calling generate_edifact()")
        self.generate_edifact(cr, uid, ids, context)

    def check_removed_edifact_files(self, cr, uid, ids=None, context=None):
        """ Check for edifact files removed from the ftp server

        This method will be called in a cron job.
        """
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        company = user.company_id
        host = company.edifact_purchase_host
        port = company.edifact_purchase_port
        ftpuser = company.edifact_purchase_user
        droppath = company.edifact_purchase_path

        ids = self.search(cr, uid, ['&', ('edifact_sent', '=', True),
                                    ('edifact_removed', '=', False)])

        to_check = self.read(cr, uid, ids, ['name'])
        removed = []

        if not host and not port:
            # assuming local path
            for rec in to_check:
                fullpath = os.path.join(droppath, '%s.edi' % rec['name'])
                if not os.path.exists(fullpath):
                    removed.append(rec['id'])
        else:
            try:
                transport = self._connect(host, port, ftpuser)
                try:
                    ftp = paramiko.SFTPClient.from_transport(transport)
                    ftp.chdir(droppath)
                    # doing it by ftp
                    listing = ftp.listdir()
                    for rec in to_check:
                        filename = '%s.edi' % rec['name']
                        if filename not in listing:
                            removed.append(rec['id'])
                finally:
                    ftp.close()
                    transport.close()
            except (paramiko.SSHException, socket.error, IOError) as err:
                raise Warning("Could not check processed purchase order EDIFACT messages on FTP server: %s" % err.message)

        if removed:
            self.write(cr, uid, removed,
                       {'edifact_removed': True}, context=context)
        return True

    def _connect(self, host, port, user):
        """ connect to ftp server """
        # Load private key for transfert
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        transport = paramiko.Transport((host, port))
        transport.connect(username=user, pkey=mykey)
        return transport

    def generate_edifact(self, cr, uid, ids, context=None):
        """ generate EDIFACT message for the selected purchase orders """
        assert len(ids) == 1   # FIXME For now one, we will do batch later

        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            _logger.debug('ORDER: %s', order.name)

        if order.edifact_sent:
            raise Warning("""EDIFACT document already sent to partner
If you need to regenerate, please ask your DBA to clear the 'edifact_sent' status on %s""" %
                          order.name)

        mapping = self._build_mapping(order)
        template = self._get_template()
        renderer = make_render_engine()

        message = renderer.render(template, mapping)

        _logger.debug('message for %r:\n%r', order.name, message)

        user = self.pool['res.users'].browse(cr, uid, uid, context)
        company = user.company_id
        host = company.edifact_purchase_host
        port = company.edifact_purchase_port
        ftpuser = company.edifact_purchase_user
        droppath = company.edifact_purchase_path

        filename = '%s.edi' % order.name
        fullpath = os.path.join(droppath, filename)

        try:
            message = message.encode('latin1')
        except UnicodeEncodeError:
            _logger.warn("""EDIFACT message contains non latin1 encodable unicode caracters, they have been replaced by '?'""")
            message = message.encode('latin1', 'replace')

        if not host and not port:
            if not os.path.exists(droppath):
                os.mkdir(droppath)
            self._save_edi(fullpath, message)
        else:
            try:
                transport = self._connect(host, port, ftpuser)
                try:
                    ftp = paramiko.SFTPClient.from_transport(transport)
                    try:
                        ftp.chdir(droppath)
                    except IOError as err:
                        raise Warning('could not cd to %r on ftp server: %s' %
                                      (droppath, err.message))
                    content = StringIO(message)
                    ftp.putfo(content, filename)
                finally:
                    ftp.close()
                    transport.close()
            except (paramiko.SSHException, socket.error) as err:
                raise Warning("could not save EDIFACT message on FTP server: %s" %
                              err.message)

        # order.edifact_sent = True
        vals = {'edifact_sent': True}
        self.write(cr, uid, [order.id], vals, context=context)
        return True

    def _build_mapping(self, order):
        """ generate data mapping needed for template rendering """

        dest_address = order.dest_address_id

        def convert_unit(name):
            if name == 'PCE':
                return 'P'
            elif name == 'KGM':
                return 'K'
            elif name == 'm':
                return 'M'
            else:
                raise NotImplementedError("mapping for uom %s" % name)

        def _gv(obj, attr):
            """ helper function for mapping values generation """
            if not obj:
                return ''
            val = getattr(obj, attr)
            return val if val else ''

        mapping = {
            'codefiliale': 'PLN',
            'siretFiliale': '52789590800012',
            'dateCmd': _gv(order, 'date_order').replace('-', ''),
            'heureCmd': _gv(order, 'create_date').split()[1].replace(':', ''),
            'codeAgence': '928',
            'siretAgence': '52789590800012',
            'siretDebonix': '49039922700035',
            'noCmd': _gv(order, 'name'),
            'refCmd': _gv(order, 'name'),
            'dateLiv': _gv(order, 'minimum_planned_date').replace('-', ''),
            'compteDebonix': '0000175000',
            # NEED REVIEW adress mapping. edifact 5*35, oerp 2*128
            'adr1': _gv(dest_address, 'name'),
            'adr2': '',
            'adr3': _gv(dest_address, 'street'),
            'adr4': '',
            'adr5': '',
            'cp': _gv(dest_address, 'zip'),
            'ville': _gv(dest_address, 'city'),
            'tel': _gv(dest_address, 'phone'),
            'fax': _gv(dest_address, 'fax'),
            'commentaire': _gv(order, 'notes'),
            'totalHT': int(order.amount_untaxed * 1000),
            'totalTVA': int(order.amount_tax * 1000),
            'totalTTC': int(order.amount_total * 1000)
        }

        order_lines = list(order.order_line)

        lines = []

        total_qty = 0
        # totalHT = 0
        for line_index, order_line in enumerate(order_lines):
            # totalHT += line['prixUnitaireNet'] * line['montantLigne']
            product = order_line.product_id
            uom = product.uom_id
            line = {
                'codag': _gv(product, 'code'),
                'libelle': _gv(product, 'name')[:70],
                'prixUnitaireNet': int(order_line.price_unit * 10000),
                'qte': int(order_line.product_qty * 1000),
                'refarticleFournisseur': _gv(product, 'code'),
                'ligne': line_index+1,
                'montantLigne': int(order_line.price_subtotal * 1000),
                'uq': convert_unit(uom.name),
                'dateLiv': order_line.date_planned.replace('-', ''),
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


def make_render_engine():
    renderer = handlebars.Renderer()

    def lj(v, width, fill=' '):
        v = unicode(v)
        return v.ljust(width, fill)

    def rj(v, width, fill=' '):
        v = unicode(v)
        return v.rjust(width, fill)

    renderer.register_helper('lj', lj)
    renderer.register_helper('rj', rj)

    return renderer
