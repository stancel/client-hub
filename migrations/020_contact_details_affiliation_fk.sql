-- Migration 020: Nullable affiliation_id FK on contact detail tables
--
-- Adds affiliation_id to contact_phones, contact_emails, and
-- contact_addresses so that employer-scoped contact details
-- (e.g. work desk line at ACME, jane@acme.com, office address)
-- can point at the specific contact_org_affiliations row.
--
-- Personal/shared rows keep affiliation_id = NULL, which is the
-- default. ON DELETE SET NULL ensures removing an affiliation
-- does not delete the underlying phone/email/address — the datum
-- is still a valid contact detail for the person.
--
-- Depends on: 019 (contact_org_affiliations must exist first)

-- ============================================================
-- contact_phones
-- ============================================================
ALTER TABLE contact_phones
    ADD COLUMN IF NOT EXISTS affiliation_id BIGINT UNSIGNED NULL AFTER contact_id;

ALTER TABLE contact_phones
    ADD KEY IF NOT EXISTS idx_cp_affiliation (affiliation_id);

-- FK guarded by INFORMATION_SCHEMA check because not all MariaDB
-- builds support "ADD CONSTRAINT ... IF NOT EXISTS" uniformly.
SET @fk_cp := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contact_phones'
      AND CONSTRAINT_NAME = 'fk_cp_affiliation'
);
SET @fk_cp_sql := IF(@fk_cp = 0,
    'ALTER TABLE contact_phones
        ADD CONSTRAINT fk_cp_affiliation FOREIGN KEY (affiliation_id)
            REFERENCES contact_org_affiliations(id) ON DELETE SET NULL',
    'SELECT 1');
PREPARE s FROM @fk_cp_sql; EXECUTE s; DEALLOCATE PREPARE s;

-- ============================================================
-- contact_emails
-- ============================================================
ALTER TABLE contact_emails
    ADD COLUMN IF NOT EXISTS affiliation_id BIGINT UNSIGNED NULL AFTER contact_id;

ALTER TABLE contact_emails
    ADD KEY IF NOT EXISTS idx_ce_affiliation (affiliation_id);

SET @fk_ce := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contact_emails'
      AND CONSTRAINT_NAME = 'fk_ce_affiliation'
);
SET @fk_ce_sql := IF(@fk_ce = 0,
    'ALTER TABLE contact_emails
        ADD CONSTRAINT fk_ce_affiliation FOREIGN KEY (affiliation_id)
            REFERENCES contact_org_affiliations(id) ON DELETE SET NULL',
    'SELECT 1');
PREPARE s FROM @fk_ce_sql; EXECUTE s; DEALLOCATE PREPARE s;

-- ============================================================
-- contact_addresses
-- ============================================================
ALTER TABLE contact_addresses
    ADD COLUMN IF NOT EXISTS affiliation_id BIGINT UNSIGNED NULL AFTER contact_id;

ALTER TABLE contact_addresses
    ADD KEY IF NOT EXISTS idx_ca_affiliation (affiliation_id);

SET @fk_ca := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contact_addresses'
      AND CONSTRAINT_NAME = 'fk_ca_affiliation'
);
SET @fk_ca_sql := IF(@fk_ca = 0,
    'ALTER TABLE contact_addresses
        ADD CONSTRAINT fk_ca_affiliation FOREIGN KEY (affiliation_id)
            REFERENCES contact_org_affiliations(id) ON DELETE SET NULL',
    'SELECT 1');
PREPARE s FROM @fk_ca_sql; EXECUTE s; DEALLOCATE PREPARE s;
