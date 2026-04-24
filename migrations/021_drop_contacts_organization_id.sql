-- Migration 021: Drop contacts.organization_id and rewrite v_contact_summary
--
-- Removes the legacy single-org FK that was replaced by the
-- contact_org_affiliations junction in migration 019. Rewrites
-- v_contact_summary to source organization info from the
-- is_primary=1 affiliation row instead of the dropped column.
-- Also surfaces role_title and department from the primary
-- affiliation for integration convenience.
--
-- Per the 3NF rule: no cached denormalized pointers that duplicate
-- a fact better expressed via the junction. Removing this column
-- is the whole point of the 019-022 migration sequence.
--
-- Depends on: 019 (affiliations backfilled), 020 (detail FKs added)
--
-- ROLLBACK: restore from pre-upgrade backup. A textual reverse
-- statement is provided in a trailing comment block for reference
-- only — do not execute it without restoring affiliation rows that
-- contained data not present in the original organization_id.

-- ============================================================
-- Drop the FK constraint, the index, and the column from contacts
-- ============================================================
SET @fk_exists := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contacts'
      AND CONSTRAINT_NAME = 'fk_contacts_org'
);
SET @drop_fk_sql := IF(@fk_exists > 0,
    'ALTER TABLE contacts DROP FOREIGN KEY fk_contacts_org',
    'SELECT 1');
PREPARE s FROM @drop_fk_sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @idx_exists := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contacts'
      AND INDEX_NAME = 'idx_contacts_org'
);
SET @drop_idx_sql := IF(@idx_exists > 0,
    'ALTER TABLE contacts DROP INDEX idx_contacts_org',
    'SELECT 1');
PREPARE s FROM @drop_idx_sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @col_exists := (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'contacts'
      AND COLUMN_NAME = 'organization_id'
);
SET @drop_col_sql := IF(@col_exists > 0,
    'ALTER TABLE contacts DROP COLUMN organization_id',
    'SELECT 1');
PREPARE s FROM @drop_col_sql; EXECUTE s; DEALLOCATE PREPARE s;

-- ============================================================
-- Rewrite v_contact_summary to use the affiliation junction
-- ============================================================
-- Organization name now comes from the is_primary=1 row in
-- contact_org_affiliations (joined through organizations). If no
-- primary affiliation exists, organization_name is NULL. Also
-- surfaces primary_role_title and primary_department from the
-- same row for integration convenience.
DROP VIEW IF EXISTS v_contact_summary;

CREATE VIEW v_contact_summary AS
SELECT
    c.id AS contact_id,
    c.uuid AS contact_uuid,
    c.first_name,
    c.last_name,
    c.display_name,
    ct.code AS contact_type,
    ct.label AS contact_type_label,
    c.enrichment_status,
    c.marketing_opt_out_sms,
    c.marketing_opt_out_email,
    c.marketing_opt_out_phone,
    c.converted_at,
    c.is_active,
    c.created_at,
    pa.primary_org_name AS organization_name,
    pa.primary_role_title,
    pa.primary_department,
    (SELECT cp.phone_number FROM contact_phones cp
        WHERE cp.contact_id = c.id AND cp.is_primary = TRUE
        LIMIT 1) AS primary_phone,
    (SELECT ce.email_address FROM contact_emails ce
        WHERE ce.contact_id = c.id AND ce.is_primary = TRUE
        LIMIT 1) AS primary_email,
    (SELECT COUNT(*) FROM orders o
        WHERE o.contact_id = c.id AND o.is_active = TRUE) AS total_orders,
    (SELECT COALESCE(SUM(o.total), 0) FROM orders o
        WHERE o.contact_id = c.id AND o.is_active = TRUE) AS lifetime_value,
    (SELECT MAX(o.order_date) FROM orders o
        WHERE o.contact_id = c.id AND o.is_active = TRUE) AS last_order_date,
    (SELECT COUNT(*) FROM communications cm
        WHERE cm.contact_id = c.id) AS total_communications,
    (SELECT MAX(cm.occurred_at) FROM communications cm
        WHERE cm.contact_id = c.id) AS last_communication_at,
    (SELECT COALESCE(SUM(i.balance_due), 0)
        FROM invoices i
        JOIN orders o ON i.order_id = o.id
        WHERE o.contact_id = c.id AND i.is_active = TRUE) AS outstanding_balance,
    (SELECT GROUP_CONCAT(ms.label ORDER BY ms.sort_order SEPARATOR ', ')
        FROM contact_marketing_sources cms
        JOIN marketing_sources ms ON cms.marketing_source_id = ms.id
        WHERE cms.contact_id = c.id) AS marketing_sources,
    (SELECT GROUP_CONCAT(t.label ORDER BY t.sort_order SEPARATOR ', ')
        FROM contact_tag_map ctm
        JOIN tags t ON ctm.tag_id = t.id
        WHERE ctm.contact_id = c.id) AS tags,
    src.code AS first_seen_source_code,
    src.name AS first_seen_source_name
FROM contacts c
JOIN contact_types ct ON c.contact_type_id = ct.id
JOIN sources src ON c.first_seen_source_id = src.id
LEFT JOIN (
    SELECT coa.contact_id,
           org.name        AS primary_org_name,
           coa.role_title  AS primary_role_title,
           coa.department  AS primary_department
    FROM contact_org_affiliations coa
    JOIN organizations org ON coa.organization_id = org.id
    WHERE coa.is_primary = TRUE
      AND coa.is_active = TRUE
) pa ON pa.contact_id = c.id;

-- ============================================================
-- ROLLBACK REFERENCE (do not execute without a data-safe plan)
-- ============================================================
--
-- To restore the dropped column (data will be incomplete — rows
-- without a primary affiliation will get NULL, and rows with
-- multiple orgs will collapse to one):
--
--   ALTER TABLE contacts ADD COLUMN organization_id BIGINT UNSIGNED NULL AFTER contact_type_id;
--   UPDATE contacts c
--     LEFT JOIN (
--       SELECT contact_id, organization_id
--       FROM contact_org_affiliations
--       WHERE is_primary = TRUE AND is_active = TRUE
--     ) pa ON pa.contact_id = c.id
--     SET c.organization_id = pa.organization_id;
--   ALTER TABLE contacts ADD KEY idx_contacts_org (organization_id);
--   ALTER TABLE contacts ADD CONSTRAINT fk_contacts_org FOREIGN KEY (organization_id)
--     REFERENCES organizations(id) ON DELETE SET NULL;
--   [and restore the prior v_contact_summary definition from migration 015]
--
-- The canonical rollback path is to restore from the pre-upgrade
-- backup rather than execute the above.
