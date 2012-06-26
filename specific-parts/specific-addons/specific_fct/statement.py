# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright 2011 Camptocamp SA
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
from osv import fields
from osv.osv import except_osv
from osv.orm import Model
from tools.translate import _
import netsvc
logger = netsvc.Logger()

class AccountStatementCompletionRule(Model):
    """
    Redifine a rule that will match SO number with AND without the prefix
    _mag that is added by OpeneRP cause the bank/office doesn't know it, so
    we have most of the time not the exact number in that case.
    """
    
    _inherit = "account.statement.completion.rule"
    
    def _get_functions(self, cr, uid, context=None):
        res = super (AccountStatementCompletionRule, self)._get_functions(
                cr, uid, context=context)
        res.append(('get_from_ref_and_so_with_prefix', 'From line reference (based on SO number with or without mag_)'))
        return res

    _columns={
        'function_to_call': fields.selection(_get_functions, 'Method'),
    }
    
    
    def get_from_ref_and_so_with_prefix(self, cursor, uid, line_id, context=None):
        """
        Match the partner based on the SO number (with and without '_mag' as prefix) 
        and the reference of the statement 
        line. Then, call the generic get_values_for_line method to complete other values. 
        If more than one partner matched, raise the ErrorTooManyPartner error.

        :param int/long line_id: id of the concerned account.bank.statement.line
        :return:
            A dict of value that can be passed directly to the write method of
            the statement line or {}
           {'partner_id': value,
            'account_id' : value,
            
            ...}
        """
        st_obj = self.pool.get('account.bank.statement.line')
        st_line = st_obj.browse(cursor,uid,line_id)
        res = {}
        if st_line:
            so_obj = self.pool.get('sale.order')
            so_id = so_obj.search(cursor, uid, [('name', '=', st_line.ref)])
            if so_id:
                if so_id and len(so_id) == 1:
                    so = so_obj.browse(cursor, uid, so_id[0])
                    res['partner_id'] = so.partner_id.id
                elif so_id and len(so_id) > 1:
                    raise ErrorTooManyPartner(_('Line named "%s" (Ref:%s) was matched by more than one partner.')%(st_line.name,st_line.ref))
                st_vals = st_obj.get_values_for_line(cursor, uid, profile_id = st_line.statement_id.profile_id.id,
                    partner_id = res.get('partner_id',False), line_type = st_line.type, amount = st_line.amount, context = context)
                res.update(st_vals)
            # Try with prefix now
            else:
                so_id = so_obj.search(cursor, uid, [('name', '=', 'mag_' + st_line.ref)])
                if so_id:
                    if so_id and len(so_id) == 1:
                        so = so_obj.browse(cursor, uid, so_id[0])
                        res['partner_id'] = so.partner_id.id
                    elif so_id and len(so_id) > 1:
                        raise ErrorTooManyPartner(_('Line named "%s" (Ref:%s) was matched by more than one partner.')%(st_line.name,st_line.ref))
                    st_vals = st_obj.get_values_for_line(cursor, uid, profile_id = st_line.statement_id.profile_id.id,
                        partner_id = res.get('partner_id',False), line_type = st_line.type, amount = st_line.amount, context = context)
                    res.update(st_vals)
        return res
    