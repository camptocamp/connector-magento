@debonix  @migration  @base

Feature: Migrate the database after the OpenERP migration

  Scenario: when we receive the database from the migration service, addons are 'to upgrade', set them to uninstalled.
    Given I execute the SQL commands
    """
    UPDATE ir_module_module set state = 'uninstalled' where state IN ('to install', 'to upgrade');
    """

  Scenario: remove the 'retry missing' flag on cron to avoid having them running again and again
    Given I execute the SQL commands
    """
    UPDATE ir_cron SET doall = false WHERE doall = true;
    """

  @custom_fields
  Scenario: delete the custom fields (x_) in openerp because they are no longer used (x_ooor_id and product attributes)
    # and they make the upgrade of modules crash
    Given I execute the SQL commands
    """
    DELETE FROM ir_model_fields WHERE name LIKE 'x\_%';
    """

  Scenario: update of modules fail when the product is there, we have to remove it anyway
    Given I execute the SQL commands
    """
    DELETE FROM delivery_carrier WHERE id in (SELECT res_id FROM ir_model_data WHERE module = 'sale_exceptions' AND name = 'no_delivery_carrier');
    DELETE FROM ir_model_data WHERE module = 'sale_exceptions' AND name = 'no_delivery_carrier';
    DELETE FROM product_template WHERE id IN (SELECT product_tmpl_id FROM product_product WHERE id in (SELECT res_id FROM ir_model_data WHERE module = 'sale_exceptions' AND name = 'no_delivery_product'));
    DELETE FROM ir_model_data WHERE module = 'sale_exceptions' AND name = 'no_delivery_product';
    DELETE FROM res_partner WHERE id in (SELECT res_id FROM ir_model_data WHERE module = 'sale_exceptions' AND name = 'no_delivery_partner');
    """

  Scenario: Clean the unused crm stages because they have xmlid linked to crm_claim modules, but the xml ids do not exist in the xml files...
    Given I execute the SQL commands
    """
    DELETE FROM crm_claim_stage WHERE NOT EXISTS (SELECT id FROM crm_claim WHERE stage_id = crm_claim_stage.id);
    """

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

  @clean
  Scenario: Remove stock picking menu entry to be replaced by filters
    Given I execute the SQL commands
    """
    DELETE FROM ir_ui_menu WHERE name = 'Colisage disponible Magasin';
    DELETE FROM ir_ui_menu WHERE name = 'Colisage Disponible Expédition';
    DELETE FROM ir_act_window WHERE name = 'Available Packing';
    DELETE FROM ir_translation WHERE name = 'ir.actions.act_window,name' AND src = 'Available Packing';
    """

  @clean
  Scenario: Remove product attribute set menu entries
    Given I execute the SQL commands
    """
    DELETE FROM ir_ui_menu
        WHERE parent_id = 110
            AND name IN
                ('Default', 'Vetements', 'vetement', 'Chauffage', 'piscine', 'quincaillerie', 'Abrasifs',
                 'Burins', 'Disques', 'Embouts', 'Forets', 'conso_electro', 'electricite', 'Fraises', 'Meches', 'Meules', 'bricodeal');

    DELETE FROM ir_act_window WHERE res_model = 'product.product' AND id IN (561,1145,1146,1147,1148,1149,1150,1151,1152,1153,1154,1155,1157,1158,1159,1160,1163);
    DELETE FROM ir_translation WHERE name = 'ir.actions.act_window,name' AND res_id IN (561,1145,1146,1147,1148,1149,1150,1151,1152,1153,1154,1155,1157,1158,1159,1160,1163);
    """

  @update_module_list
  Scenario: Update module list before updating to avoid draging old dependancies
  Given I update the module list

  @uninstall
  Scenario: uninstall addons wrongly installed during migration
    Given I uninstall the following modules:
      | name               |
      | mrp_jit            |
      | project_mrp        |
      | project            |
      | portal             |
      | document_ftp       |
      | product_links      |

  Scenario: install main addons
    Given I install the required modules with dependencies:
      | name               |
      | base               |
    Then my modules should have been installed and models reloaded

  Scenario: remove the size limit on procurement_order.message (has been modified in ocb, not sure if the update do it, in doubt. remove it)
    Given I execute the SQL commands
    """
    ALTER TABLE procurement_order ALTER message TYPE varchar;
    """

  Scenario: Fix the order_policy on sales orders: 'postpaid' does no longer exist
    Given I execute the SQL commands
    """
    UPDATE sale_order SET order_policy = 'manual' WHERE order_policy = 'postpaid';
    """

  Scenario: Fix the order_policy default value on sales orders: 'postpaid' does no longer exist
    Given I execute the SQL commands
    """
    UPDATE ir_values SET value = E'S''manual''\np0\n.' WHERE id = 633;
    """

  Scenario: Delete the 'Packing' related action on sales orders that do not work
    Given I execute the SQL commands
    """
    delete from ir_actions where id = 1776;
    delete from ir_values where id = 1533;
    """
