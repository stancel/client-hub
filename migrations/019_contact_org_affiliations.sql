-- Migration 019: contact_org_affiliations junction + seniority_levels lookup
--
-- Introduces proper many-to-many modeling between contacts and
-- organizations with per-affiliation attributes (role_title,
-- department, seniority, dates, decision-maker, primary flag).
-- Backfills from the existing contacts.organization_id column so
-- no data is lost before migration 021 drops that column.
--
-- Enforces "at most one primary affiliation per contact" at the DB
-- level via a VIRTUAL generated column (is_primary_key) combined
-- with a composite UNIQUE index. NULL values do not count toward
-- uniqueness in InnoDB/MariaDB, so non-primary rows are
-- unconstrained while at most one row may have is_primary=TRUE.
--
-- See docs/data-model.rst "contact_org_affiliations" section and
-- docs/Migration-Strategy.rst for rationale.
--
-- Depends on: contacts, organizations
-- Followed by: 020 (detail affiliation_id), 021 (drop contacts.organization_id), 022 (detail primary uniqueness)

-- ============================================================
-- seniority_levels lookup table
-- ============================================================
CREATE TABLE IF NOT EXISTS seniority_levels (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    label VARCHAR(100) NOT NULL,
    sort_order INT UNSIGNED NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY ux_seniority_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO seniority_levels (code, label, sort_order)
VALUES
    ('exec',    'Executive / C-Suite',      10),
    ('senior',  'Senior / Director',        20),
    ('mid',     'Mid-Level / Manager',      30),
    ('junior',  'Junior / Individual',      40),
    ('intern',  'Intern',                   50),
    ('unknown', 'Unknown / Not Specified',  99)
ON DUPLICATE KEY UPDATE
    label = VALUES(label),
    sort_order = VALUES(sort_order);

-- ============================================================
-- contact_org_affiliations junction table
-- ============================================================
CREATE TABLE IF NOT EXISTS contact_org_affiliations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    contact_id BIGINT UNSIGNED NOT NULL,
    organization_id BIGINT UNSIGNED NOT NULL,
    role_title VARCHAR(200) NULL,
    department VARCHAR(100) NULL,
    seniority_level_id BIGINT UNSIGNED NULL,
    is_decision_maker BOOLEAN NOT NULL DEFAULT FALSE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    is_primary_key TINYINT UNSIGNED GENERATED ALWAYS AS (IF(is_primary, 1, NULL)) VIRTUAL,
    start_date DATE NULL,
    end_date DATE NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    notes_text TEXT NULL,
    external_refs_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    UNIQUE KEY idx_coa_uuid (uuid),
    KEY idx_coa_contact (contact_id),
    KEY idx_coa_org (organization_id),
    KEY idx_coa_active (contact_id, is_active),
    UNIQUE KEY ux_coa_one_primary (contact_id, is_primary_key),
    CONSTRAINT fk_coa_contact FOREIGN KEY (contact_id)
        REFERENCES contacts(id) ON DELETE CASCADE,
    CONSTRAINT fk_coa_org FOREIGN KEY (organization_id)
        REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT fk_coa_seniority FOREIGN KEY (seniority_level_id)
        REFERENCES seniority_levels(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Backfill from contacts.organization_id
-- ============================================================
-- Only runs if the legacy column still exists (i.e. 021 hasn't
-- applied yet). NOT EXISTS predicate makes the insert idempotent —
-- re-running 019 will not create duplicate rows for contacts that
-- were already backfilled on a prior invocation.
SET @has_legacy_org_id := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contacts'
      AND COLUMN_NAME = 'organization_id'
);

SET @backfill_sql := IF(@has_legacy_org_id > 0,
    'INSERT INTO contact_org_affiliations
         (uuid, contact_id, organization_id, is_primary, is_active, created_by)
     SELECT UUID(), c.id, c.organization_id, TRUE, TRUE, ''migration_019_backfill''
     FROM contacts c
     WHERE c.organization_id IS NOT NULL
       AND NOT EXISTS (
           SELECT 1 FROM contact_org_affiliations coa
           WHERE coa.contact_id = c.id
             AND coa.organization_id = c.organization_id
       )',
    'SELECT 1'
);

PREPARE backfill_stmt FROM @backfill_sql;
EXECUTE backfill_stmt;
DEALLOCATE PREPARE backfill_stmt;
