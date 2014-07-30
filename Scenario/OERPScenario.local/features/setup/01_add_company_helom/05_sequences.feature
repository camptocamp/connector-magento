@helom_init @helom_sequences

Feature: set sequences on new stock picking models (in, int, out)

  Scenario Outline: set sequences on new stock picking models (in, int, out)
    Given I find a "ir.sequence" with name: <name>
    Then I set their values to:
      | key                | value           |
      | prefix             | <prefix>        |
      | padding            | <padding>       |
      | number_next_actual | <number>        |
      | code               | <code> |
      | company_id		   | <company_id> |

    Examples: on stock picking sequences
      | name        | prefix | padding | number | code | company_id |
          | Stock Tracking Lots                     |                                |        5 |        1 | stock.lot.tracking          |        2 | 
          | Payment Line                            |                                |        5 |        1 | payment.line                |        2 | 
          | Payment order                           | OP%(year)s/                    |        5 |        1 | payment.order               |        2 | 
          | Production order                        | OP                             |        5 |        1 | mrp.production              |        2 | 
          | Stock Production Lots                   |                                |        5 |        1 | stock.lot.serial            |        2 | 
          | Account Bank Statement                  | RB%(year)s                     |        5 |        1 | account.bank.statement      |        2 | 
          | Stock orderpoint                        | OP/                            |        5 |        1 | mrp.warehouse.orderpoint    |        2 | 
          | Picking INT                             | int_                           |        5 |        1 | stock.picking               |        2 | 
          | Sale Journal                            | SAJ/%(year)s/                  |        5 |        1 | account.journal             |        2 | 
          | Sales Credit Note Journal               | SCNJ/%(year)s/                 |        5 |        1 | account.journal             |        2 | 
          | Purchase Journal                        | EXJ/%(year)s/                  |        5 |        1 | account.journal             |        2 | 
          | Expenses Credit Notes Journal           | ECNJ/%(year)s/                 |        5 |        1 | account.journal             |        2 | 
          | Bank Journal                            | BNK/%(year)s/                  |        5 |        1 | account.journal             |        2 | 
          | Checks Journal                          | CHK/%(year)s/                  |        5 |        1 | account.journal             |        2 | 
          | Cash Journal                            | CSH/%(year)s/                  |        5 |        1 | account.journal             |        2 | 
          | Cash Receipt                            | %(year)s/                      |        5 |        1 | rec_voucher                 |        2 | 
          | Cash Payment                            | %(year)s/                      |        5 |        1 | pay_voucher                 |        2 | 
          | Bank Receipt                            | %(year)s/                      |        5 |        1 | bank_rec_voucher            |        2 | 
          | Bank Payment                            | %(year)s/                      |        5 |        1 | bank_pay_voucher            |        2 | 
          | Contra Entry                            | %(year)s/                      |        5 |        1 | cont_voucher                |        2 | 
          | Sales Entry                             | %(year)s/                      |        5 |        1 | journal_sale_vou            |        2 | 
          | Purchase Entry                          | %(year)s/                      |        5 |        1 | journal_pur_vou             |        2 | 
          | Picking OUT                             | p                              |        5 |        1 | stock.picking.out           |        2 | 
          | Account Refund In                       | AC%(y)s%(month)s               |        5 |        1 | account.invoice.in_refund   |        2 | 
          | Purchase Order                          | CF%(y)s%(month)s               |        5 |        1 | purchase.order              |        2 | 
          | Stock orderpoint                        | OP/                            |        5 |        1 | stock.orderpoint            |        2 | 
          | Account reconcile sequence              | LET                            |        5 |        1 | account.reconcile           |        2 | 
          | Account Journal                         |                                |        5 |        1 | account.journal             |        2 | 
          | Account Refund Out                      | AF%(y)s%(month)s               |        5 |        1 | account.invoice.out_refund  |        2 | 
          | Account Invoice In                      | FF%(y)s%(month)s               |        5 |        1 | account.invoice.in_invoice  |        2 | 
          | Account Invoice Out                     | FC%(y)s%(month)s               |        5 |        1 | account.invoice.out_invoice |        2 | 
          | Picking IN                              | in_                            |        5 |        1 | stock.picking.in            |        2 | 
 
      