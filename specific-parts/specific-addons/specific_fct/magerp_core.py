# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright 2011 Camptocamp SA
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

from osv import osv, fields
from magentoerpconnect import magerp_osv
from base_external_referentials import external_osv

DEBUG = False

class external_referential(magerp_osv.magerp_osv):
    _inherit = "external.referential"

    def sync_partner(self, cr, uid, ids, ctx):
        instances = self.browse(cr, uid, ids, ctx)

        for inst in instances:
            attr_conn = self.external_connection(cr, uid, inst, DEBUG)
            first_iteration = True
            next_customer_id = False
            
            while first_iteration or next_customer_id:
                first_iteration = False
                
# customer.list_by_slices documentation        
# Input :         
#    {'first_id'  : int = null (optional),
#     'nbrclient' : int = 1000 (optional)}
# Output :
#     {'customers'        : {entity_id : {customer_infos}},
#      'next_customer_id' : int || false}

                customer_result = attr_conn.call('customer.list_by_slices', [{'first_id': next_customer_id, 'nbrclient': 1000}])
                
                result = []
                result_address = []

                list_customer = customer_result['customers'] # customers list
                next_customer_id = customer_result['next_customer_id'] # returns False when no more customers
                
                for customer_id in list_customer:
                    customer_id = int(customer_id)

                    each_customer_info = attr_conn.call('customer.info', [customer_id])
                    result.append(each_customer_info)

                    each_customer_address_info = attr_conn.call('customer_address.list', [customer_id])
                    customer_address_info = each_customer_address_info[0]
                    customer_address_info['customer_id'] = customer_id
                    customer_address_info['email'] = each_customer_info['email']
                    result_address.append(customer_address_info)

                partner_ids = self.pool.get('res.partner').ext_import(cr, uid, result, inst.id, context={})
                partner_address_ids = self.pool.get('res.partner.address').ext_import(cr, uid, result_address, inst.id, context={})

        return True
    
external_referential() 
