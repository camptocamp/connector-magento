###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@helom_init @helom_security
Feature: MULTICOMPANY SECURITY RULES TO DESACTIVATE IN ORDER TO SHARE FOLLOWING OBJECTS

  @helom_multicompany_security_rules
  Scenario: MULTICOMPANY SECURITY RULES
     Given I need a "ir.rule" with name: "multi-company currency rule"
     And having:
     | name              | value     |
     | active            | false     |

  @helom_multicompany_security_rules
  Scenario: MULTICOMPANY SECURITY RULES FOR PARTNER
     Given I need a "ir.rule" with name: "res.partner company"
     And having:
     | name              | value     |
     | domain_force            | ['|',('company_id','=',False),('company_id','child_of',[user.company_id.id])]  |

