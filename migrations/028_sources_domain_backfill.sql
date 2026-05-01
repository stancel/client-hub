-- Migration 028: Backfill sources.domain for the seeded consumer-site sources
--
-- The ``sources.domain`` column has existed since migration 014 but the
-- per-VPS install scripts never set a value, so both prod instances
-- (Complete Dental Care, Clever Orchid) carry NULL. The
-- marketing-source derivation in v0.3.0 can use the column to
-- authoritatively classify same-domain referrers as 'website' instead
-- of relying on the heuristic, and future fleet observability
-- queries (e.g. "list every instance and its consumer site domain")
-- want a non-NULL value here too.
--
-- Each UPDATE is keyed by ``code`` and gated on ``domain IS NULL`` so
-- the migration is:
--   - VPS-safe: only the matching source row on each VPS gets touched
--     (the CO update is a no-op on CDC and vice versa)
--   - Idempotent: a re-run does nothing if domain has already been set
--   - Forward-compatible: adding a new client site means adding its
--     own UPDATE here in the next migration, not editing this one

UPDATE sources
   SET domain = 'completedentalcarecolumbia.com'
 WHERE code = 'complete_dental_care_website'
   AND domain IS NULL;

UPDATE sources
   SET domain = 'cleverorchid.com'
 WHERE code = 'clever_orchid_website'
   AND domain IS NULL;

-- Migration 028 complete.
