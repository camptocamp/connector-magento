# -*- coding: utf-8 -*-
@upgrade_to_1.2.14 @debonix

Feature: upgrade to 1.2.14

  Scenario: upgrade application version
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                 |
      | debonix_purchase_edi |
      | specific_fct         |
      | specific_magento     |
    Then my modules should have been installed and models reloaded

  Scenario: change UoM on products + add keys on UoMs
    Given I execute the SQL commands
    """
        UPDATE product_uom
        SET magento_name = 'PCE', edi_code = 'P'
        WHERE id = 1;
        UPDATE product_uom
        SET magento_name = 'M', edi_code = 'M'
        WHERE id = 3;

        UPDATE product_template
        SET uom_id = 3, uom_po_id= 3
        WHERE id IN (
            SELECT product_tmpl_id
            FROM product_product
            WHERE default_code IN (
                '14472878', '14476067', '14476083', '14476105', '37260436',
                '37260444', '37260452', '37260460', '37260479', '37260487',
                '37260495', '37260541', '37260568', '37260576', '37260606',
                '37260649', '37260703', '37260762', '37260770', '37260800',
                '37260843', '37260851', '37260878', '37260894', '40187057',
                '40187073', '41298553', '41298588', '41298626', '45027902',
                '45027910', '45027929', '48159583', '48159656', '53649238',
                '53649246', '53649254', '53649262', '53649270', '53649289',
                '53649297', '53649300', '56785655'
            )
        );
    """

    Given I set the version of the instance to "1.2.14"
