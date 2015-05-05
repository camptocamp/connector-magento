@debonix @migration @picking_sequences

Feature: set sequences on new stock picking models (in, int, out)

  Scenario Outline: set sequences on new stock picking models (in, int, out)
    Given I find a "ir.sequence" with name: <name>
    Then I set their values to:
      | key                | value           |
      | prefix             | <prefix>        |
      | padding            | <padding>       |
      | number_next_actual | <number>        |
      | code               | <code> |

    Examples: on stock picking sequences
      | name        | prefix | padding | number | code                   |
      | Picking IN  | in_    | 5       | 1      | stock.picking.in       |
      | Picking INT | int_   | 5       | 1      | stock.picking.internal |

    Given I execute the SQL commands
    """
    UPDATE ir_sequence
    SET prefix = 'p',
        padding = 6,
        number_next = (SELECT REPLACE(MAX(name), 'p', '')::int + 1
                       FROM stock_picking
                       WHERE name LIKE 'p%')
    WHERE name = 'Picking OUT';
    """
