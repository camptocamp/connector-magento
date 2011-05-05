# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

import time
from report import report_sxw
from osv import osv
import pooler

class shipping(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(shipping, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'hide_partner_name': self._hide_partner_name,            
        })

    def _hide_partner_name(self, partner_obj):
        """ Define if the partner name must be displayed according to the
        list configured on the company.
        Return true if name must be hidden
        """
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid)
        company = user.company_id
        if partner_obj.title and partner_obj.title in [x.shortcut for x in company.report_hide_partner_title_ids]:
            return True
        return False

report_sxw.report_sxw('report.sale.shipping_custom','stock.picking','addons/specific_report/report/shipping.rml',parser=shipping)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
