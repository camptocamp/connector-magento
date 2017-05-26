# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Charline Dumontet
#    Copyright 2017 Camptocamp SA
#    All the methods have been duplicated from import_tracking module
#    to not take the risk to impact the actual working developments
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
from openerp.tools.translate import _
import openerp.pooler as pooler
import os
from contextlib import closing
import logging
import csv
import shutil

_logger = logging.getLogger(__name__)


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

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
                        cr, uid, purchase_order_ids, context=context):
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

    def import_colissimo_tracking_references(self, cr, uid, context=None):
        """ Read the Colissimo files and update
            the stock picking with the tracking reference
        """
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        path = company.colissimo_file_path_in
        archive_path = company.colissimo_archive_path
        error_path = company.colissimo_error_path
        if not path:
            return False
        if not os.path.exists(path):
            raise orm.except_orm(
                _('Error'),
                _('Path %s for the Colissimo tracking numbers does not '
                  'exist') % path)
        if not os.path.exists(archive_path):
            raise orm.except_orm(
                _('Error'),
                _('Archive path %s for the Colissimo tracking numbers does '
                  'not exist') % path)
        if not os.path.exists(error_path):
            raise orm.except_orm(
                _('Error'),
                _('Error path %s for the Colissimo tracking numbers does not '
                  'exist') % path)
        _logger.info('Started to import tracking number files')
        # read each file and each line in directory
        total = 0
        imported = 0
        db = pooler.get_db(cr.dbname)
        files = (f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f)))
        with closing(db.cursor()) as local_cr:
            file_error = False
            for filename in files:
                total += 1
                filepath = os.path.join(path, filename)
                try:
                    file_error = self._import_colissimo_tracking_from_file(
                        local_cr, uid, filepath, context=context)
                except Exception as err:
                    local_cr.rollback()
                    _logger.exception(
                        "Tracking file %s could not be imported",
                        filepath
                    )
                    message = (_("Tracking file %s could not be "
                                 "imported due to: %s") % (filepath, err))
                    file_error = True
                    self._manage_colissimo_errors(cr, uid, errors=message,
                                                  context=context)
                from_path = os.path.join(path, filename)
                if file_error:
                    to_path = os.path.join(error_path, filename)
                else:
                    to_path = os.path.join(archive_path, filename)
                shutil.move(from_path, to_path)
                # commit so if next file fails we won't lose
                # the imported trackings
                imported += 1
                local_cr.commit()

        _logger.info('Processed %s tracking files out of %s. %s files '
                     'with errors.', imported, total, total - imported)
        return True

    def _import_colissimo_tracking_from_file(self, cr, uid, filepath,
                                             context=None):
        _logger.info('Started to import tracking number file %s', filepath)
        file_error = False
        with open(filepath, 'r') as trackfile:
            reader = csv.reader(trackfile, delimiter=';')
            line_nb = 0
            for line in reader:
                if not line:  # handle empty lines
                    continue
                # Ignore first line
                if line_nb == 0:
                    line_nb += 1
                    continue
                try:
                    tracking_ref = line[0].strip()
                    packing_name = line[1].strip()
                except IndexError:
                    message = ("Tracking file %s could not be read at "
                               "line %s. Import of file canceled.")
                    _logger.exception(message, filepath, line)
                    self._manage_colissimo_errors(
                        cr, uid, errors=_(message) % (filepath, line),
                        context=context)
                    raise
                if packing_name:
                    file_error = self._update_colissimo_tracking_references(
                        cr, uid, packing_name, tracking_ref,
                        context=context)
                    if file_error:
                        break
        return file_error

    def _update_colissimo_tracking_references(self, cr, uid, packing_name,
                                              tracking_ref, context=None):
        """
            Update the tracking reference of the picking
        """
        picking_out_obj = self.pool['stock.picking.out']
        # In Odoo we have picking name like "p4545" and in the file there are
        # name like 'P4545' so we use lower and upper
        picking_ids = picking_out_obj.search(
            cr, uid,
            ['|', ('name', '=', packing_name.lower()),
             ('name', '=', packing_name.upper())],
            context=context)
        file_error = False
        if not picking_ids:
            self._manage_colissimo_errors(
                cr, uid, no_picking=True, errors=packing_name, context=context)
            file_error = True
        for picking in picking_out_obj.browse(cr, uid, picking_ids,
                                              context=context):
            write_ref = ''
            if picking.carrier_tracking_ref and \
                    tracking_ref not in picking.carrier_tracking_ref:
                write_ref = '%s;%s' % (picking.carrier_tracking_ref or '',
                                       tracking_ref)
            elif not picking.carrier_tracking_ref:
                write_ref = '%s' % (tracking_ref)
            if write_ref:
                picking_out_obj.write(
                    cr, uid,
                    picking_ids,
                    {'carrier_tracking_ref': write_ref},
                    context=context)

        return file_error

    def _create_colissimo_claim_errors(self, cr, uid, no_picking=False,
                                       errors='', context=None):
        """
            Create a claim if there is an error with the label
        """
        __, categ_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'delivery_carrier_file_colissimo',
            'categ_claim_colissimo_incident')
        if no_picking:
            description = _("The picking %s can't be found") % (errors)
            name = _('Expedition error %s') % (errors)
        else:
            description = errors
            name = _('Error on colissimo tracking file')
        claim_vals = {'name': name,
                      'description': description,
                      'categ_id': categ_id,
                      'claim_type': 'other'}
        claim_id = self.pool['crm.claim'].create(cr, uid, claim_vals,
                                                 context=context)
        return claim_id

    def _manage_colissimo_errors(self, cr, uid, no_picking=False,
                                 errors='', context=None):
        claim_id = self._create_colissimo_claim_errors(cr, uid, no_picking, errors,
                                            context=context)
        if claim_id:
            self._send_mail_colissimo_errors(cr, uid, claim_id, context=context)
        return True

    def _send_mail_colissimo_errors(self, cr, uid, claim_id, context=None):
        """
            Send a mail if there is an error with the colissimo import
        """
        data_obj = self.pool['ir.model.data']
        email_obj = self.pool['email.template']
        __, template_id = data_obj.get_object_reference(
            cr, uid, 'delivery_carrier_file_colissimo',
            'colissimo_import_error_template_mail')
        email_obj.send_mail(cr, uid, template_id, claim_id, context=context)
        return True