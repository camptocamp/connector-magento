# -*- coding: utf-8 -*-
from contextlib import closing, contextmanager
from support import *
from support.tools import model


@contextmanager
def newcr(ctx):
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']
    pool = openerp.modules.registry.RegistryManager.get(db_name)
    with closing(pool.db.cursor()) as cr:
        try:
            yield cr
        except:
            cr.rollback()
            raise
        else:
            cr.commit()


@given('I press the button "{button}"')
def impl(ctx, button):
    backend = ctx.found_item
    assert backend
    getattr(backend, button)()


@given('I recompute the magento stock quantities without export')
def impl(ctx):
    backend = ctx.found_item
    assert backend
    backend.update_product_stock_qty(context={'connector_no_export': True})


@given('I migrate the payment methods')
def impl(ctx):
    with newcr(ctx) as cr:
        cr.execute("SELECT name, check_if_paid, "
                   " journal_id, validate_order, "
                   " invoice_date_is_order_date, "
                   " payment_term_id, packing_priority, "
                   " days_before_order_cancel "
                   "FROM base_sale_payment_type ")
        rows = cr.dictfetchall()
    types = []
    for row in rows:
        if ';' in row['name']:
            for name in row['name'].split(';'):
                lrow = row.copy()
                lrow['name'] = name
                types.append(lrow)
        else:
            types.append(row)
    AutoWorkflow = model('sale.workflow.process')
    PaymentMethod = model('payment.method')
    ModelData = model('ir.model.data')
    manual = AutoWorkflow.get('sale_automatic_workflow.manual_validation')
    automatic = AutoWorkflow.get('sale_automatic_workflow.automatic_validation')
    for ptype in types:
        if ptype['validate_order']:
            wkf = automatic
        else:
            wkf = manual
        if ptype['check_if_paid']:
            import_rule = 'paid'
        else:
            import_rule = 'always'
        vals = {'name': ptype['name'],
                'journal_id': ptype['journal_id'],
                'workflow_process_id': wkf.id,
                'import_rule': import_rule,
                'days_before_cancel': 0,
                'payment_term_id': ptype['payment_term_id'],
                # level has changed from 1 level
                'picking_priority': str(int(ptype['packing_priority'] or 2) - 1),
                }
        xmlid = 'scenario.method_%s' % ptype['name']
        method = PaymentMethod.get(xmlid)
        if method:
            method.write(vals)
        else:
            method = PaymentMethod.create(vals)
            module, xmlid = xmlid.split('.', 1)
            _model_data = ModelData.create({'name': xmlid,
                                            'model': 'payment.method',
                                            'res_id': method.id,
                                            'module': module,
                                            })


@given('I set the new payment methods on the sales orders')
def impl(ctx):
    PaymentMethod = model('payment.method')
    with newcr(ctx) as cr:
        cr.execute("SELECT name "
                   "FROM base_sale_payment_type ")
        rows = cr.fetchall()
    ptypes = []
    for row in rows:
        name = row[0]
        if ';' in name:
            for lname in name.split(';'):
                ptypes.append(lname)
        else:
            ptypes.append(row[0])

    with newcr(ctx) as cr:
        for ptype in ptypes:
            method = PaymentMethod.get([('name', '=', ptype)])
            cr.execute("UPDATE sale_order "
                       "SET payment_method_id = %s, "
                       "    workflow_process_id = %s "
                       "WHERE ext_payment_method = %s "
                       "AND payment_method_id IS NULL ",
                       (method.id, method.workflow_process_id.id, ptype))
        cr.execute("UPDATE account_invoice "
                   "SET workflow_process_id = so.workflow_process_id "
                   "FROM sale_order so, sale_order_invoice_rel rel "
                   "WHERE account_invoice.workflow_process_id IS NULL "
                   "AND so.id = rel.order_id "
                   "AND account_invoice.id = rel.invoice_id ")
        cr.execute("UPDATE stock_picking "
                   "SET workflow_process_id = so.workflow_process_id "
                   "FROM sale_order so "
                   "WHERE stock_picking.workflow_process_id IS NULL "
                   "AND so.id = stock_picking.sale_id ")
