# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import base64
import csv

from osv import fields, osv
from tools.translate import _

class ChronopostLine(object):
    fields = (('subaccount', 3),
              ('client_code', 15),
              ('name1', 35),
              ('name2', 35),
              ('street1', 35),
              ('street2', 35),
              ('zip', 5),
              ('city', 30),
              ('country', 2),
              ('phone', 20),
              ('email', 35),
              ('ref1', 20),
              ('ref2', 20),
              ('weight', 6),
              ('chrono_product', 3),                                                                   
              ('saturday_delivery', 1),
              ('insurance_amount', 8),
              ('rep_amount', 8),
              ('customs_amount', 8),                                  
              )

    def __init__(self):
        [setattr(self, field_name, '') for field_name, width in self.fields]

    def get_fields(self):
       res = []
       [res.append(getattr(self, field_name)[0:width]) for field_name, width in self.fields]
       return res


class StockCsvColissimo(osv.osv):
    """ Inherit stock picking to export the csv when a picking is done """
    _inherit = 'stock.picking'

    _columns = {
        'carrier_tracking_ref':fields.char('Carrier Tracking Reference', size=32),
        'cash_on_delivery_amount': fields.float('Cash on delivery amount', help='Put the amount to be used for the packing cash on delivery with chronopost.'),
        'cash_on_delivery_amount_untaxed': fields.float('Cash on delivery amount untaxed', help='Put the untaxed amount to be used for the packing cash on delivery with chronopost.'),        
        'package_number': fields.integer('Number of packaging', help='Choose the number of packaging you want, this will generate this number of line in the Chronopost file..'),
        'nextorder_id': fields.one2many('stock.picking', 'backorder_id', 'Next Order ID', readonly=True), # the next packing id (reverse of back order)
    }
    
    _defaults = {
        'package_number': lambda * a: 1,
    }
    
    def _write_csv(self, filename, content=None):
        """
        Write a CSV file with the content given in the parameter
        """
        if not content:
            content = []

        fid = open(filename, 'w')
        writer = csv.writer(fid, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in content:
            writer.writerow([field.encode("utf-8") for field in row.get_fields()])
        fid.close()
        # chronopost needs to drop the file so we have to put the write permission on the group
        os.chmod(filename, 0664)
        return True

    def create_chronopost_file(self, cr, uid, ids, context=None):
        """
        Export a fixed width file with the picking informations
        """
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id

        if not company.tracking_csv_path_out:
            raise osv.except_osv(_("Chronopost Error"), _("The path where the CSV files are generated is not configured in the company setup."))

        if not os.path.exists(company.tracking_csv_path_out):
            raise osv.except_osv(_("Chronopost Error"), _("The path configured in the company setup where the CSV files are generated does not exist on the server."))

        if not company.chronopost_subaccount_number:
            raise osv.except_osv(_("Chronopost Error"), _("The Chronopost Sub-Account number is not configured in the company setup."))

        
        for packing in self.browse(cr, uid, ids, context):
            # only create a csv for out packings with transporter
            if packing.type == 'out' and packing.carrier_id:
                # generate file content
                file = []
                filename = "%s.txt" % packing.name
                line = ChronopostLine()

                line.subaccount = company.chronopost_subaccount_number
                line.client_code = packing.address_id and str(packing.address_id.partner_id.id) or ''
                line.name1 = packing.address_id and packing.address_id.name or ''
                line.street1 = packing.address_id and packing.address_id.street or ''
                line.street2 = packing.address_id and packing.address_id.street2 or ''
                line.zip = packing.address_id and packing.address_id.zip or ''
                line.city = packing.address_id and packing.address_id.city or ''
                line.country = packing.address_id and packing.address_id.country_id.code or ''
                line.phone = packing.address_id and packing.address_id.phone or ''
                line.email = packing.address_id and packing.address_id.email or ''
                line.ref1 = packing.name
                line.ref2 = packing.sale_id and packing.sale_id.name or ''
                line.weight = "%.2f" % self._get_packing_weight(cr, uid, packing)
                line.chrono_product = packing.carrier_id and packing.carrier_id.chronopost_code and packing.carrier_id.chronopost_code or ''
                line.saturday_delivery = 'L'
                line.insurance_amount = '0.00'
                amount = self._get_n_update_amount_cash_by_delivery(cr, uid, company, packing)
                line.rep_amount = amount['taxed'] and "%.2f" % amount['taxed'] or '0.00'
                line.customs_amount =  amount['untaxed'] and "%.2f" % amount['untaxed'] or '0.00'
                number_of_line = packing.package_number > 0 and packing.package_number or 1
                for x in range(number_of_line):
                    file.append(line)

                self._write_csv(os.path.join(company.tracking_csv_path_out, filename), file)
        return True

    def action_done(self, cr, uid, ids, context=None):
        """
        Overriding of the stock picking, function called when the picking is done.
        """
        self.create_chronopost_file(cr, uid, ids, context=context)
        return super(StockCsvColissimo, self).action_done(cr, uid, ids, context)

    def _get_packing_weight(self, cr, uid, packing):
        """Returns the weight of a packing for colissimo"""
        # minimal value is 0.5 kg if any product of the packing contains a weight
        weight = 0.5
        if packing.weight != 0.0:
            weight = packing.weight
        return weight

    def _get_n_update_amount_cash_by_delivery(self,cr, uid, company, packing):
        # [amount, untaxed amount]
        amount = {'taxed': False, 'untaxed': False}
        # First rule: if cash_on_delivery amount, then take it
        if packing.cash_on_delivery_amount != 0.0 or packing.cash_on_delivery_amount_untaxed != 0.0:
            amount['taxed'] = packing.cash_on_delivery_amount
            amount['untaxed'] = packing.cash_on_delivery_amount_untaxed
        else:
            # Get amount if "contre-remboursement" payment method +
            # those methodes are define into the company !
            if company.cash_on_delivery_method and packing.sale_id.ext_payment_method:
                # Look if this packing must be "contre-remboursement"
                if packing.sale_id.ext_payment_method in company.cash_on_delivery_method.split(';'):
                    # Look if already one packing for the order that has been done
                    # If yes, then ignore the cash_by_delivery for this one
                    done_pack_ids=self.pool.get('stock.picking').search(cr,uid,[('id','in',[x.id for x in packing.sale_id.picking_ids]),('state','=','done')])
                    if not done_pack_ids:
                        amount['taxed'] = packing.sale_id.amount_total
                        amount['untaxed'] = packing.sale_id.amount_untaxed 
                        self.write(cr, uid, packing.id, {'cash_on_delivery_amount': amount['taxed'], 
                                                         'cash_on_delivery_amount_untaxed': amount['untaxed']})
        return amount

    def _update_tracking_references(self, cr, uid, packing_name, tracking_ref, context=None):
        """ Update the tracking reference of a packing """
        # tracking reference is updated only for packing (Outgoing Products)
        # update only tracking references not already set
        found_packing = self.search(cr, uid, [('name', '=', packing_name),
                                              ('type', '=', 'out'),
                                              ('carrier_tracking_ref', '=', False),
                                              ('state', '=', 'done')], context=context)
        packing = self.browse(cr, uid, found_packing, context)
        if packing:
            self.write(cr, uid, packing[0].id, {'carrier_tracking_ref': tracking_ref})

    def import_tracking_references(self, cr, uid, context=None):
        """ Read the Chronopost file and update the stock picking with the tracking reference """

        # get company
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id

        if not company.tracking_csv_path_in or not os.path.exists(company.tracking_csv_path_in):
            return

        # read each file and each line in directory
        for root, dirs, files in os.walk(company.tracking_csv_path_in, topdown=False):
            for f in files:
                ofile = open(os.path.join(root, f), 'r')
                reader = csv.reader(ofile, delimiter=';')
                updated = False
                try:
                    for line in reader:
                        # read fields 
                        tracking_ref = line[1].strip()
                        packing_name = line[6].strip()

                        if packing_name:
                            self._update_tracking_references(cr, uid, packing_name, tracking_ref, context)
                            updated = True
                finally:
                    ofile.close()
                    
                # delete the file if the tracking references have been updated
                if updated:
                    os.unlink(os.path.join(root, f))

    def run_import_tracking_references_scheduler(self, cr, uid, context=None):
        """ Scheduler for import tracking references """
        self.import_tracking_references(cr, uid, context)


    def write(self, cr, uid, ids, vals, context=None):
        #cash on delivery must only apply on the first packing
        if 'backorder_id' in vals:
            vals['cash_on_delivery_amount'] = 0.0
            vals['cash_on_delivery_amount_untaxed'] = 0.0
        return super(StockCsvColissimo, self).write(cr, uid, ids, vals, context=context)

StockCsvColissimo()
