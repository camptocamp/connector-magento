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
from osv import osv, fields
from tools.translate import _
import netsvc
logger = netsvc.Logger()

class AccountBankStatement(osv.osv):

    _inherit = "account.bank.statement"

    def button_confirm(self, cr, uid, ids, context={}):
        """Overriding statement in order to have better error management
           We have to rewrite a big block of code"""
        done = []
        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = \
                self.pool.get('account.bank.statement.line')

        company_currency_id = res_users_obj.browse(cr, uid, uid,
                context=context).company_id.currency_id.id

        for st in self.browse(cr, uid, ids, context):
            if not st.state=='draft':
                continue

            if not (abs(st.balance_end - st.balance_end_real) < 0.0001):
                raise osv.except_osv(_('Error !'),
                        _('The statement balance is incorrect !\n') +
                        _('The expected balance (%.2f) is different than the computed one. (%.2f)') % (st.balance_end_real, st.balance_end))
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configuration Error !'),
                        _('Please verify that an account is defined in the journal.'))
            invalid_lines = []
            for line in st.move_line_ids:
                if line.state <> 'valid':
                    invalid_lines.append(line.name)
            if invalid_lines:
                raise osv.except_osv(
                    _('Error !'),
                    _('The following account entries lines are not in valid state. : %s') % (u', '.join(invalid_lines)))
            # for bank.statement.lines
            # In line we get reconcile_id on bank.ste.rec.
            # in bank stat.rec we get line_new_ids on bank.stat.rec.line
            error_stack = []
            for move in st.line_ids:
                try:
                    context.update({'date':move.date})
                    move_id = account_move_obj.create(cr, uid, {
                        'journal_id': st.journal_id.id,
                        'period_id': st.period_id.id,
                        'date': move.date,
                    }, context=context)
                    account_bank_statement_line_obj.write(cr, uid, [move.id], {
                        'move_ids': [(4,move_id, False)]
                    })
                    if not move.amount:
                        continue

                    torec = []
                    if move.amount >= 0:
                        account_id = st.journal_id.default_credit_account_id.id
                    else:
                        account_id = st.journal_id.default_debit_account_id.id
                    acc_cur = ((move.amount<=0) and st.journal_id.default_debit_account_id) or move.account_id
                    amount = res_currency_obj.compute(cr, uid, st.currency.id,
                            company_currency_id, move.amount, context=context,
                            account=acc_cur)
                    if move.reconcile_id and move.reconcile_id.line_new_ids:
                        for newline in move.reconcile_id.line_new_ids:
                            amount += newline.amount

                    val = {
                        'name': move.name,
                        'date': move.date,
                        'ref': move.ref,
                        'move_id': move_id,
                        'partner_id': ((move.partner_id) and move.partner_id.id) or False,
                        'account_id': (move.account_id) and move.account_id.id,
                        'credit': ((amount>0) and amount) or 0.0,
                        'debit': ((amount<0) and -amount) or 0.0,
                        'statement_id': st.id,
                        'journal_id': st.journal_id.id,
                        'period_id': st.period_id.id,
                        'currency_id': st.currency.id,
                    }
                
                    amount = res_currency_obj.compute(cr, uid, st.currency.id,
                            company_currency_id, move.amount, context=context,
                            account=acc_cur)
                    #if st.currency.id <> company_currency_id:
                    amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                                st.currency.id, amount, context=context,
                                account=acc_cur)
                    val['amount_currency'] = -amount_cur

                    if move.account_id and move.account_id.currency_id and move.account_id.currency_id.id <> company_currency_id:
                        val['currency_id'] = move.account_id.currency_id.id
                        amount_cur = res_currency_obj.compute(cr, uid, company_currency_id,
                                move.account_id.currency_id.id, amount, context=context,
                                account=acc_cur)
                        val['amount_currency'] = -amount_cur

                    torec.append(account_move_line_obj.create(cr, uid, val , context=context))

                    if move.reconcile_id and move.reconcile_id.line_new_ids:
                        for newline in move.reconcile_id.line_new_ids:
                            account_move_line_obj.create(cr, uid, {
                                'name': newline.name or move.name,
                                'date': move.date,
                                'ref': move.ref,
                                'move_id': move_id,
                                'partner_id': ((move.partner_id) and move.partner_id.id) or False,
                                'account_id': (newline.account_id) and newline.account_id.id,
                                'debit': newline.amount>0 and newline.amount or 0.0,
                                'credit': newline.amount<0 and -newline.amount or 0.0,
                                'statement_id': st.id,
                                'journal_id': st.journal_id.id,
                                'period_id': st.period_id.id,

                            }, context=context)

                    # Fill the secondary amount/currency
                    # if currency is not the same than the company
                    amount_currency = False
                    currency_id = False
                    #if st.currency.id <> company_currency_id:
                    amount_currency = move.amount
                    currency_id = st.currency.id
                    account_move_line_obj.create(cr, uid, {
                        'name': move.name,
                        'date': move.date,
                        'ref': move.ref,
                        'move_id': move_id,
                        'partner_id': ((move.partner_id) and move.partner_id.id) or False,
                        'account_id': account_id,
                        'credit': ((amount < 0) and -amount) or 0.0,
                        'debit': ((amount > 0) and amount) or 0.0,
                        'statement_id': st.id,
                        'journal_id': st.journal_id.id,
                        'period_id': st.period_id.id,
                        'amount_currency': amount_currency,
                        'currency_id': currency_id,
                        }, context=context)
                    for line in account_move_line_obj.browse(cr, uid, [x.id for x in
                            account_move_obj.browse(cr, uid, move_id,
                                context=context).line_id],
                            context=context):
                        if line.state <> 'valid':
                            raise osv.except_osv(_('Error !'),
                                    _('Account move line "%s" is not valid') % line.name)

                    if move.reconcile_id and move.reconcile_id.line_ids:
                        ## Search if move has already a partial reconciliation
                        previous_partial = False
                        for line_reconcile_move in move.reconcile_id.line_ids:
                            if line_reconcile_move.reconcile_partial_id:
                                previous_partial = True
                                break
                        ##
                        torec += map(lambda x: x.id, move.reconcile_id.line_ids)
                        #try:
                        if abs(move.reconcile_amount-move.amount)<0.0001:

                            writeoff_acc_id = False
                            #There should only be one write-off account!
                            for entry in move.reconcile_id.line_new_ids:
                                writeoff_acc_id = entry.account_id.id
                                break
                            ## If we have already a partial reconciliation
                            ## We need to make a partial reconciliation
                            ## To add this amount to previous paid amount
                            if previous_partial:
                                account_move_line_obj.reconcile_partial(cr, uid, torec, 'statement', context)
                            ## If it's the first reconciliation, we do a full reconciliation as regular
                            else:
                                account_move_line_obj.reconcile(cr, uid, torec, 'statement', writeoff_acc_id=writeoff_acc_id, writeoff_period_id=st.period_id.id, writeoff_journal_id=st.journal_id.id, context=context)

                        else:
                            account_move_line_obj.reconcile_partial(cr, uid, torec, 'statement', context)
                        #except:
                        #    raise osv.except_osv(_('Error !'), _('Unable to reconcile entry "%s": %.2f') % (move.name, move.amount))

                    if st.journal_id.entry_posted:
                        account_move_obj.write(cr, uid, [move_id], {'state':'posted'})
                except osv.except_osv, exc:
                    msg = "%s had following error %s" % (move.id, exc.value)
                    error_stack.append(msg)
                    logger.notifyChannel("Statement confirmation",
                                         netsvc.LOG_ERROR,
                                         msg)
                except Exception, exc:
                    msg = "%s had following error %s" % (move.id, str(exc))
                    error_stack.append(msg)
                    logger.notifyChannel("Statement confirmation",
                                         netsvc.LOG_ERROR,
                                         msg)
            if error_stack:
                msg = u"\n".join(error_stack)
                raise osv.except_osv(_('Error !'), msg)
            done.append(st.id)
        self.write(cr, uid, done, {'state':'confirm'}, context=context)
        return True

AccountBankStatement()