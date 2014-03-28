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
