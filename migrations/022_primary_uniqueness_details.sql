-- Migration 022: DB-level enforcement of "at most one is_primary=TRUE per contact"
-- on contact_phones, contact_emails, and contact_addresses
--
-- The existing schema had no DB-level guard preventing two rows in
-- a detail table from both being marked is_primary=TRUE for the
-- same contact. That invariant was service-layer-only and could be
-- violated by direct-SQL writers (MCP tools, operator scripts,
-- future SaaS operator connections). This migration closes the
-- gap using the same generated-column pattern already used on
-- contact_org_affiliations in migration 019.
--
-- Pattern: a VIRTUAL generated column is_primary_key = IF(is_primary, 1, NULL)
-- combined with a composite UNIQUE index on (contact_id, is_primary_key).
-- Because NULL values do not participate in UNIQUE constraints under
-- InnoDB/MariaDB, non-primary rows (where is_primary_key is NULL) are
-- unconstrained; at most one row per contact may have is_primary_key=1.
--
-- Service-layer still enforces the companion "at least one primary
-- when any rows exist" invariant on create/update/delete paths.
--
-- Depends on: 020 (affiliation_id columns; not functionally required
-- but 022 is bundled with the multi-org release)
--
-- PRE-APPLY GUARD: if existing data already violates "at most one
-- primary per contact," this migration will fail. The pre-apply
-- block below demotes duplicates (keeping the lowest-id row as
-- primary, setting the rest to is_primary=FALSE) to make the
-- migration safe to run on any existing database.

-- ============================================================
-- Pre-apply: demote duplicate primaries if any exist
-- ============================================================
UPDATE contact_phones cp
JOIN (
    SELECT contact_id, MIN(id) AS keep_id
    FROM contact_phones
    WHERE is_primary = TRUE
    GROUP BY contact_id
    HAVING COUNT(*) > 1
) dupes ON cp.contact_id = dupes.contact_id
SET cp.is_primary = FALSE
WHERE cp.is_primary = TRUE AND cp.id <> dupes.keep_id;

UPDATE contact_emails ce
JOIN (
    SELECT contact_id, MIN(id) AS keep_id
    FROM contact_emails
    WHERE is_primary = TRUE
    GROUP BY contact_id
    HAVING COUNT(*) > 1
) dupes ON ce.contact_id = dupes.contact_id
SET ce.is_primary = FALSE
WHERE ce.is_primary = TRUE AND ce.id <> dupes.keep_id;

UPDATE contact_addresses ca
JOIN (
    SELECT contact_id, MIN(id) AS keep_id
    FROM contact_addresses
    WHERE is_primary = TRUE
    GROUP BY contact_id
    HAVING COUNT(*) > 1
) dupes ON ca.contact_id = dupes.contact_id
SET ca.is_primary = FALSE
WHERE ca.is_primary = TRUE AND ca.id <> dupes.keep_id;

-- ============================================================
-- contact_phones: is_primary_key generated column + UNIQUE index
-- ============================================================
ALTER TABLE contact_phones
    ADD COLUMN IF NOT EXISTS is_primary_key TINYINT UNSIGNED
        GENERATED ALWAYS AS (IF(is_primary, 1, NULL)) VIRTUAL
        AFTER is_primary;

SET @ux_cp := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contact_phones'
      AND INDEX_NAME = 'ux_cp_one_primary'
);
SET @sql_ux_cp := IF(@ux_cp = 0,
    'ALTER TABLE contact_phones
        ADD UNIQUE KEY ux_cp_one_primary (contact_id, is_primary_key)',
    'SELECT 1');
PREPARE s FROM @sql_ux_cp; EXECUTE s; DEALLOCATE PREPARE s;

-- ============================================================
-- contact_emails: is_primary_key generated column + UNIQUE index
-- ============================================================
ALTER TABLE contact_emails
    ADD COLUMN IF NOT EXISTS is_primary_key TINYINT UNSIGNED
        GENERATED ALWAYS AS (IF(is_primary, 1, NULL)) VIRTUAL
        AFTER is_primary;

SET @ux_ce := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contact_emails'
      AND INDEX_NAME = 'ux_ce_one_primary'
);
SET @sql_ux_ce := IF(@ux_ce = 0,
    'ALTER TABLE contact_emails
        ADD UNIQUE KEY ux_ce_one_primary (contact_id, is_primary_key)',
    'SELECT 1');
PREPARE s FROM @sql_ux_ce; EXECUTE s; DEALLOCATE PREPARE s;

-- ============================================================
-- contact_addresses: is_primary_key generated column + UNIQUE index
-- ============================================================
ALTER TABLE contact_addresses
    ADD COLUMN IF NOT EXISTS is_primary_key TINYINT UNSIGNED
        GENERATED ALWAYS AS (IF(is_primary, 1, NULL)) VIRTUAL
        AFTER is_primary;

SET @ux_ca := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contact_addresses'
      AND INDEX_NAME = 'ux_ca_one_primary'
);
SET @sql_ux_ca := IF(@ux_ca = 0,
    'ALTER TABLE contact_addresses
        ADD UNIQUE KEY ux_ca_one_primary (contact_id, is_primary_key)',
    'SELECT 1');
PREPARE s FROM @sql_ux_ca; EXECUTE s; DEALLOCATE PREPARE s;
