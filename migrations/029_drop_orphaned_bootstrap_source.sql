-- Migration 029: drop orphaned ``bootstrap`` source rows
--
-- The seeded ``bootstrap`` source carries this description:
--
--     "Initial source created by the installer.
--      Rename or create additional sources as needed."
--
-- On a correctly-configured install the operator either renames it
-- (one-tenant case) or creates a properly-named consumer-site source
-- alongside it (multi-source case) and never uses the ``bootstrap``
-- code at runtime. In that second case the ``bootstrap`` row is left
-- behind as a vestige with no api_keys, no contacts, and no
-- communications referencing it — that's the state on Complete
-- Dental Care today.
--
-- This migration removes those orphans only. The DELETE is gated on
-- "no inbound FK reference at all" so it's:
--
--   - Idempotent: re-running on a clean install is a no-op
--   - Fleet-safe: a VPS where ``bootstrap`` *is* still the live
--     source (e.g. Clever Orchid before its rename) is untouched
--   - Forward-compatible: future installs that always create a
--     properly-named source up front have nothing to clean up here
--
-- The rename of an *active* ``bootstrap`` row (the CO case) is not
-- attempted here because the new code/name/domain are per-install
-- values — see ``scripts/rename-bootstrap-source.sql`` for that.

DELETE FROM sources
 WHERE code = 'bootstrap'
   AND id NOT IN (SELECT DISTINCT source_id FROM api_keys
                   WHERE source_id IS NOT NULL)
   AND id NOT IN (SELECT DISTINCT first_seen_source_id FROM contacts
                   WHERE first_seen_source_id IS NOT NULL)
   AND id NOT IN (SELECT DISTINCT source_id FROM communications
                   WHERE source_id IS NOT NULL)
   AND id NOT IN (SELECT DISTINCT source_id FROM spam_events
                   WHERE source_id IS NOT NULL)
   AND id NOT IN (SELECT DISTINCT source_id FROM spam_rate_log
                   WHERE source_id IS NOT NULL);

-- Migration 029 complete.
