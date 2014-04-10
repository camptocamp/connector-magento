@debonix  @migration  @base

Feature: Migrate the database after the OpenERP migration

  Scenario: when we receive the database from the migration service, addons are 'to upgrade', set them to uninstalled.
    Given I execute the SQL commands
    """
    UPDATE ir_module_module set state = 'uninstalled' where state IN ('to install', 'to upgrade');
    """

  @custom_fields
  Scenario: delete the custom fields (x_) in openerp because they are no longer used (x_ooor_id and product attributes)
    # and they make the upgrade of modules crash
    Given I execute the SQL commands
    """
    DELETE FROM ir_model_fields WHERE name LIKE 'x\_%';
    """

  Scenario: update of modules fail when the product is there, we have to remove it anyway
    Given I find a "delivery.carrier" with oid: sale_exceptions.no_delivery_carrier
    Then I delete it
    Given I find a "product.product" with oid: sale_exceptions.no_delivery_product
    Then I delete it
    Given I find a "res.partner" with oid: sale_exceptions.no_delivery_partner
    Then I delete it

  @clean
  Scenario: clean the stuff of old modules
    Given I delete all the ir.ui.view records created by uninstalled modules
    And I delete all the ir.ui.menu records created by uninstalled modules
    And I delete all the ir.act_window records created by uninstalled modules
    And I delete all the ir.actions.act_window records created by uninstalled modules
    And I delete all the ir.actions.act_window.view records created by uninstalled modules
    And I delete all the ir.actions.wizard records created by uninstalled modules
    And I delete all the ir.act.report.xml records created by uninstalled modules
    And I delete all the ir.actions.todo records created by uninstalled modules
    And I delete all the ir.cron records created by uninstalled modules
    And I delete all the ir.module.repository records created by uninstalled modules
    And I delete all the ir.report.custom records created by uninstalled modules
    And I delete all the ir.report.custom.fields records created by uninstalled modules
    And I delete all the ir.ui.view_sc records created by uninstalled modules
    And I delete all the ir.values records created by uninstalled modules
    And I delete all the ir.rule records created by uninstalled modules
    And I delete all the ir.rule.group records created by uninstalled modules
    And I delete the broken ir.values

  Scenario: Remove stock picking menu entry to be replaced by filters
    Given I execute the SQL commands
    """
    DELETE FROM ir_ui_menu WHERE name = 'Colisage disponible Magasin';
    DELETE FROM ir_ui_menu WHERE name = 'Colisage Disponible Expédition';
    DELETE FROM ir_act_window WHERE name = 'Available Packing';
    DELETE FROM ir_translation WHERE name = 'ir.actions.act_window,name' AND src = 'Available Packing';
    """

  Scenario: Remove product attribute set menu entries
    Given I execute the SQL commands
    """
    DELETE FROM ir_ui_menu
        WHERE parent_id = 110
            AND name IN
                ('Default', 'Vetements', 'vetement', 'Chauffage', 'piscine', 'quincaillerie', 'Abrasifs',
                 'Burins', 'Disques', 'Embouts', 'Forets', 'conso_electro', 'electricite', 'Fraises', 'Meches', 'Meules');

    DELETE FROM ir_act_window WHERE res_model = 'product.product' AND id IN (561,1145,1146,1147,1148,1149,1150,1151,1152,1153,1154,1155,1157,1158,1159,1160);
    DELETE FROM ir_translation WHERE name = 'ir.actions.act_window,name' AND res_id IN (561,1145,1146,1147,1148,1149,1150,1151,1152,1153,1154,1155,1157,1158,1159,1160);
    """

  Scenario: install main addons
    Given I install the required modules with dependencies:
      | name               |
      | base               |
    Then my modules should have been installed and models reloaded
