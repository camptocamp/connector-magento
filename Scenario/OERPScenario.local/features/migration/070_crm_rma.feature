@debonix  @migration  @rma

Feature: install various modules

  Scenario: install addons
    Given I install the required modules with dependencies:
      | name        |
      | openerp_rma |
    Then my modules should have been installed and models reloaded

  Scenario: remove bad ir_model_data as claim have there own stage class
    Given I execute the SQL commands
    """
    DELETE FROM ir_model_data
      WHERE
        module = 'crm_claim'
      AND
        model = 'crm.case.stage'
      AND
        name IN (
        'stage_claim1',
        'stage_claim2',
        'stage_claim3',
        'stage_claim5');
    """

  Scenario Outline: ensure crm_stages exists
    Given I need a "crm.claim.stage" with oid: <oid>
    And having:
      | name         | value      |
      | name         | <name>     |
      | state        | <state>    |
      | sequence     | <sequence> |
      | case_default | True       |

    Examples:
      | oid                    | name        | state | sequence |
      | crm_claim.stage_claim1 | New         | draft | 26       |
      | crm_claim.stage_claim5 | In Progress | open  | 27       |
      | crm_claim.stage_claim2 | Settled     | done  | 28       |

  Scenario Outline: ensure crm_stages exists
    Given I need a "crm.claim.stage" with oid: <oid>
    And having:
      | name         | value      |
      | name         | <name>     |
      | state        | <state>    |
      | sequence     | <sequence> |
      | case_default | True       |
      | case_refused | True       |
      | fold         | True       |

    Examples:
      | oid                    | name     | state  | sequence |
      | crm_claim.stage_claim3 | Rejected | cancel | 29       |

  @clean_claim_stage
  Scenario Outline: Map old stages to new stages
    Given I execute the SQL commands
    """
    UPDATE crm_claim SET state = '<new_state>', stage_id = model_data.res_id
        FROM (SELECT res_id FROM ir_model_data WHERE module = 'crm_claim' AND model = 'crm.claim.stage' AND name = '<new_stage>') AS model_data
        WHERE stage_id = <stage> AND state = '<state>';
    """
    Examples:
      | state   | stage | new_state | new_stage    |
      | draft   | 24    | open      | stage_claim5 |
      | draft   | 28    | draft     | stage_claim1 |
      | draft   | 29    | open      | stage_claim5 |
      | draft   | 30    | open      | stage_claim5 |
      | draft   | 31    | open      | stage_claim5 |
      | draft   | 32    | open      | stage_claim5 |
      | draft   | 33    | open      | stage_claim5 |
      | draft   | 34    | open      | stage_claim5 |
      | open    | 4     | open      | stage_claim5 |
      | pending | 45    | open      | stage_claim5 |
      | done    | 5     | done      | stage_claim2 |
      | cancel  | 6     | cancel    | stage_claim3 |

  @remove_old_claim_stages
  Scenario: Remove obsolete claim stages
    Given I execute the SQL commands
    """
    DELETE FROM crm_claim_stage WHERE id NOT IN
      (SELECT res_id FROM ir_model_data
      WHERE module = 'crm_claim' AND model = 'crm.claim.stage'
            AND name IN ('stage_claim1', 'stage_claim2', 'stage_claim3', 'stage_claim5'))
    """
