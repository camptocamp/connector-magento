# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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


class ResCompany(orm.Model):
    """override company to add config for stock it"""
    _inherit = "res.company"

    _columns = {
        'stockit_base_path': fields.char('Base Path', size=256),
        'stockit_in_picking_export': fields.char('Ingoing Picking Export Folder', size=32),
        'stockit_in_picking_import': fields.char('Ingoing Picking Import Folder', size=32),
        'stockit_out_picking_export': fields.char('Outgoing Picking Export Folder', size=32),
        'stockit_out_pick_exp_location_id': fields.many2one('stock.location', 'Outgoing Picking Export Location'),
        'stockit_inventory_import': fields.char('Inventory Import Folder', size=32),
        'stockit_product_export': fields.char('Product Export Folder', size=32),
        'stockit_product_ean_export': fields.char('Product EAN13 Export Folder', size=32),
        'stockit_in_picking_location_id': fields.many2one('stock.location', 'Ingoing Picking Default Source Location', required=True),
        'stockit_in_picking_location_dest_id': fields.many2one('stock.location', 'Ingoing Picking Default Dest. Location', required=True),
        'stockit_inventory_location_id': fields.many2one('stock.location', 'Inventory Default Location', required=True),
    }
