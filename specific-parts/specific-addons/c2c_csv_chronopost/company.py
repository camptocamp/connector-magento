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

from osv import fields, osv
from tools.translate import _

class ResCompany(osv.osv):
    """inherit company to add csv chronopost configuration"""
    _inherit = "res.company"
    _columns = {
        'tracking_csv_path_out':fields.char('Path for outgoing CSV files', 
                                            size=256, 
                                            required=True, 
                                            help='Absolute path where the CSV files will be created when a packing is done.'),
        'tracking_csv_path_in':fields.char('Path for ingoing CSV files', 
                                           size=256, 
                                           required=True, 
                                           help='Absolute path where the CSV files will be read to update the tracking reference.'),
        'cash_on_delivery_method':fields.char('Cash on delivery method',
                                            size=256,
                                            help='Magento Payment methode code for cash on delivery type of payments (ex. casheondelivery;remboursement). All packing from order with those payments methodes\
                                            will complete the last field of the generated file for chronopost'),
        'chronopost_subaccount_number': fields.char('Chronopost subaccount number',
                                                    size=3,
                                                    help='Subaccount number of the company. This number is output at the 3 first positions on the csv.')
    }
    
    def _check_tracking_csv_path(self, cr, uid, ids):
        for company in self.browse(cr, uid, ids):
            if not company.tracking_csv_path_out or not company.tracking_csv_path_in:
                continue
            if company.tracking_csv_path_in == company.tracking_csv_path_out:
                return False
        return True
                
    _constraints = [(_check_tracking_csv_path, 'Error: Tracking CSV path for ingoing and outgoing files cannot be the same path.', ['tracking_csv_path_out', 'tracking_csv_path_in'])]

    
ResCompany()
