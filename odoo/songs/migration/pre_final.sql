-- See explanations on `pre.sql`.

UPDATE
    ir_module_module
SET
    state = REPLACE(state, 'install_or_update_later_', '')
WHERE
    state like 'install_or_update_later_%';
