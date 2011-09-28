# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
#
# Author : Guewen Baconnier (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv
from tools.translate import _

class CreateChronopostFile(osv.osv_memory):

    _name = 'stock.create.chronopost.file'

    def create_chronopost_file(self, cr, uid, ids, context=None):
        """
        Call the creation of a chronopost file on the selected packing(s)
        """
        context = context or {}
        pickings_ids = context.get('active_ids')
        if not pickings_ids:
            raise osv.except_osv(_('Error'), _('No packing selected'))

        picking_obj = self.pool.get('stock.picking')

        done_picking_ids = [picking.id for picking
                            in picking_obj.browse(cr, uid, pickings_ids, context=context)
                            if picking.state == 'done']

        if not done_picking_ids:
            raise osv.except_osv(_('Error'), _('No done packing selected'))

        picking_obj.create_chronopost_file(cr, uid, done_picking_ids, context=context)

        return {'type': 'ir.actions.act_window_close'}


CreateChronopostFile()
