-- One-shot: rename the ``bootstrap`` source to a properly-named
-- consumer-site source. Used when an install left ``bootstrap`` in
-- place as the only source rather than creating a properly-named
-- one up front (the historic Clever Orchid install case).
--
-- BEFORE RUNNING: edit the four placeholder values below, OR (better)
-- copy this file under a per-VPS name like
-- ``rename-bootstrap-clever-orchid.sql`` so the values are committed
-- alongside the action.
--
-- Safe to run because the rename is in-place — ``id`` stays the same
-- so every FK (api_keys.source_id, contacts.first_seen_source_id,
-- communications.source_id, spam_events.source_id,
-- spam_rate_log.source_id) continues to resolve. ``code`` is UNIQUE
-- so the rename collides if a row with the new code already exists,
-- which is the right failure mode (caller should investigate).
--
-- The WHERE on ``code = 'bootstrap'`` makes a re-run a no-op once the
-- rename has been applied.
--
-- Usage:
--
--   docker exec -i clienthub-mariadb \
--     mariadb -uroot -p"$ROOT_PW" clienthub \
--     < scripts/rename-bootstrap-source.sql
--
-- Going forward, ``scripts/install.sh`` should be updated to create
-- a properly-named source from day one (operator supplies code,
-- name, domain) so this script is never needed for a *new* install
-- — only for fixing the ones that pre-date that change.

UPDATE sources
   SET code        = 'REPLACE_ME_e_g_clever_orchid_website',
       name        = 'REPLACE_ME_e_g_Clever Orchid Website',
       source_type = 'website',
       domain      = 'REPLACE_ME_e_g_cleverorchid.com',
       description = NULL
 WHERE code = 'bootstrap';
