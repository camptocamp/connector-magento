# -*- coding: utf-8 -*-
@upgrade_from_1.1.9 @debonix

Feature: upgrade to 1.1.10

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | product_price_history                |
      | product_cost_incl_bom_price_history  |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- clean up before inserting
    DELETE FROM product_price_history;

    -- insert at Jan 1st 1900, to be sure value is set in the past.
    INSERT INTO product_price_history (
        create_uid,
        write_uid,
        company_id,
        create_date,
        write_date,
        datetime,
        name,
        amount,
        product_id
    ) SELECT
        1,
        1,
        1,
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        '1900-01-01 00:00:00',
        'cost_price',
        cost_price,
        product_tmpl_id
    FROM product_product;

    INSERT INTO product_price_history (
        create_uid,
        write_uid,
        company_id,
        create_date,
        write_date,
        datetime,
        name,
        amount,
        product_id
    ) SELECT
        1,
        1,
        1,
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        '1900-01-01 00:00:00',
        'list_price',
        list_price,
        id
    FROM product_template;

    INSERT INTO product_price_history (
        create_uid,
        write_uid,
        company_id,
        create_date,
        write_date,
        datetime,
        name,
        amount,
        product_id
    ) SELECT
        1,
        1,
        1,
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        '1900-01-01 00:00:00',
        'standard_price',
        standard_price,
        id
    FROM product_template;

    -- insert with date now() to have a more solid date
    INSERT INTO product_price_history (
        create_uid,
        write_uid,
        company_id,
        create_date,
        write_date,
        datetime,
        name,
        amount,
        product_id
    ) SELECT
        1,
        1,
        1,
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        'cost_price',
        cost_price,
        product_tmpl_id
    FROM product_product;

    INSERT INTO product_price_history (
        create_uid,
        write_uid,
        company_id,
        create_date,
        write_date,
        datetime,
        name,
        amount,
        product_id
    ) SELECT
        1,
        1,
        1,
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        'list_price',
        list_price,
        id
    FROM product_template;

    INSERT INTO product_price_history (
        create_uid,
        write_uid,
        company_id,
        create_date,
        write_date,
        datetime,
        name,
        amount,
        product_id
    ) SELECT
        1,
        1,
        1,
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
        'standard_price',
        standard_price,
        id
    FROM product_template;
    """

    Given I set the version of the instance to "1.1.10"
