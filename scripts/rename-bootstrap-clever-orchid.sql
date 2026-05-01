-- One-shot: rename the ``bootstrap`` source on the Clever Orchid VPS
-- to ``clever_orchid_website``. See the parameterized template at
-- ``scripts/rename-bootstrap-source.sql`` for the rationale.
--
-- This file carries the actual Clever Orchid values committed for
-- audit so a future reader can see exactly what was applied.
--
-- Run once, on CO only:
--
--   ssh root@165.245.130.39 \
--     'docker exec -i clienthub-mariadb mariadb -uroot -p"$PW" clienthub' \
--     < scripts/rename-bootstrap-clever-orchid.sql
--
-- After this runs, the row's ``id`` stays at 1 — every dependent FK
-- (api_keys, contacts.first_seen_source_id, communications.source_id,
-- spam_events.source_id, spam_rate_log.source_id) continues to
-- resolve unchanged. Only ``code``, ``name``, ``source_type``,
-- ``domain``, and ``description`` change.
--
-- Idempotent: a re-run on a row that's already been renamed is a
-- zero-row UPDATE.

UPDATE sources
   SET code        = 'clever_orchid_website',
       name        = 'Clever Orchid Website',
       source_type = 'website',
       domain      = 'cleverorchid.com',
       description = NULL
 WHERE code = 'bootstrap';
