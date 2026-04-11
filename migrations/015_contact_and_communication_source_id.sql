-- Migration 015: Add source_id columns to contacts and communications
-- Backfills existing rows with the bootstrap source.

-- Add first_seen_source_id to contacts
ALTER TABLE contacts ADD COLUMN first_seen_source_id BIGINT UNSIGNED NULL AFTER contact_type_id;
UPDATE contacts
  SET first_seen_source_id = (SELECT id FROM sources WHERE code = 'bootstrap')
  WHERE first_seen_source_id IS NULL;
ALTER TABLE contacts MODIFY COLUMN first_seen_source_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE contacts ADD KEY idx_contacts_first_seen_source (first_seen_source_id);
ALTER TABLE contacts ADD CONSTRAINT fk_contacts_first_seen_source
    FOREIGN KEY (first_seen_source_id) REFERENCES sources(id) ON DELETE RESTRICT;

-- Add source_id to communications
ALTER TABLE communications ADD COLUMN source_id BIGINT UNSIGNED NULL AFTER id;
UPDATE communications
  SET source_id = (SELECT id FROM sources WHERE code = 'bootstrap')
  WHERE source_id IS NULL;
ALTER TABLE communications MODIFY COLUMN source_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE communications ADD KEY idx_communications_source (source_id);
ALTER TABLE communications ADD CONSTRAINT fk_communications_source
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;

-- Re-create views with source info
DROP VIEW IF EXISTS v_contact_summary;
DROP VIEW IF EXISTS v_contact_last_order;

CREATE OR REPLACE VIEW v_contact_last_order AS
SELECT
    c.id AS contact_id,
    c.uuid AS contact_uuid,
    o.uuid AS last_order_uuid,
    o.order_number AS last_order_number,
    o.order_date AS last_order_date,
    os.code AS last_order_status,
    o.total AS last_order_total,
    (
        SELECT GROUP_CONCAT(DISTINCT oit.code ORDER BY oit.sort_order SEPARATOR ', ')
        FROM order_items oi2
        JOIN order_item_types oit ON oi2.item_type_id = oit.id
        WHERE oi2.order_id = o.id
    ) AS last_order_item_types,
    (
        SELECT GROUP_CONCAT(oi3.description ORDER BY oi3.sort_order SEPARATOR '; ')
        FROM order_items oi3
        WHERE oi3.order_id = o.id
    ) AS last_order_items_description,
    src.code AS first_seen_source_code,
    src.name AS first_seen_source_name
FROM contacts c
JOIN orders o ON o.contact_id = c.id
    AND o.id = (
        SELECT o2.id FROM orders o2
        WHERE o2.contact_id = c.id AND o2.is_active = TRUE
        ORDER BY o2.order_date DESC, o2.id DESC
        LIMIT 1
    )
JOIN order_statuses os ON o.order_status_id = os.id
JOIN sources src ON c.first_seen_source_id = src.id;

CREATE OR REPLACE VIEW v_contact_summary AS
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
    org.name AS organization_name,
    (SELECT cp.phone_number FROM contact_phones cp WHERE cp.contact_id = c.id AND cp.is_primary = TRUE LIMIT 1) AS primary_phone,
    (SELECT ce.email_address FROM contact_emails ce WHERE ce.contact_id = c.id AND ce.is_primary = TRUE LIMIT 1) AS primary_email,
    (SELECT COUNT(*) FROM orders o WHERE o.contact_id = c.id AND o.is_active = TRUE) AS total_orders,
    (SELECT COALESCE(SUM(o.total), 0) FROM orders o WHERE o.contact_id = c.id AND o.is_active = TRUE) AS lifetime_value,
    (SELECT MAX(o.order_date) FROM orders o WHERE o.contact_id = c.id AND o.is_active = TRUE) AS last_order_date,
    (SELECT COUNT(*) FROM communications cm WHERE cm.contact_id = c.id) AS total_communications,
    (SELECT MAX(cm.occurred_at) FROM communications cm WHERE cm.contact_id = c.id) AS last_communication_at,
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
LEFT JOIN organizations org ON c.organization_id = org.id
JOIN sources src ON c.first_seen_source_id = src.id;
