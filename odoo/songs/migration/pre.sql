-- Reset 'state' of ir_module_module
--
-- When we receive the database from the migration service, some addons are
-- 'to install' or 'to upgrade', set them to 'install_or_update_later'.
--
-- The goal is to allow us play all songs we need to fix data without
-- attempt to Odoo to install or update modules.
--
-- And in `pre_final.sql`, we rollback the state like it was setted previously.
--
-- With that change, in migration.yml file,
-- we need to add all modules we want to keep installed.

UPDATE
    ir_module_module
SET
    state = 'install_or_update_later_' || state
WHERE
    state IN ('to install', 'to upgrade');
