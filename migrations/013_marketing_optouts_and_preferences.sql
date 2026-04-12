-- Migration 013: Marketing opt-out flags, contact preferences, summary views
-- Data-first: these are available at the DB level, not just through the API.

-- ==========================================================================
-- 1. Explicit marketing opt-out boolean flags on contacts
-- ==========================================================================
-- Simple 1/0 flags for compliance. These are the authoritative opt-out
-- flags — the contact_channel_prefs table provides more granular detail.

ALTER TABLE contacts
    ADD COLUMN marketing_opt_out_sms BOOLEAN NOT NULL DEFAULT FALSE AFTER enrichment_status,
    ADD COLUMN marketing_opt_out_email BOOLEAN NOT NULL DEFAULT FALSE AFTER marketing_opt_out_sms,
    ADD COLUMN marketing_opt_out_phone BOOLEAN NOT NULL DEFAULT FALSE AFTER marketing_opt_out_email;

ALTER TABLE contacts
    ADD KEY idx_contacts_optout_sms (marketing_opt_out_sms),
    ADD KEY idx_contacts_optout_email (marketing_opt_out_email),
    ADD KEY idx_contacts_optout_phone (marketing_opt_out_phone);

-- ==========================================================================
-- 2. Contact preferences (flexible key-value per contact)
-- ==========================================================================
-- Stores arbitrary preferences: preferred contact time, language,
-- special instructions, communication frequency, etc.

CREATE TABLE IF NOT EXISTS contact_preferences (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    contact_id BIGINT UNSIGNED NOT NULL,
    pref_key VARCHAR(100) NOT NULL,
    pref_value TEXT NOT NULL,
    data_source VARCHAR(50) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_cp_contact_key (contact_id, pref_key),
    KEY idx_cp_contact (contact_id),
    KEY idx_cp_key (pref_key),
    CONSTRAINT fk_cpref_contact FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================================================
-- 3. View: Last order summary per contact
-- ==========================================================================
-- Data-first: queryable directly via SQL. Returns one row per contact
-- with their most recent order details.

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
    ) AS last_order_items_description
FROM contacts c
JOIN orders o ON o.contact_id = c.id
    AND o.id = (
        SELECT o2.id FROM orders o2
        WHERE o2.contact_id = c.id AND o2.is_active = TRUE
        ORDER BY o2.order_date DESC, o2.id DESC
        LIMIT 1
    )
JOIN order_statuses os ON o.order_status_id = os.id;

-- ==========================================================================
-- 4. View: Comprehensive contact intelligence summary
-- ==========================================================================
-- One row per contact with lifetime stats, marketing flags, last activity.
-- This is the "holistic view" — join this to get a full picture.

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
    -- Primary contact details
    (SELECT cp.phone_number FROM contact_phones cp WHERE cp.contact_id = c.id AND cp.is_primary = TRUE LIMIT 1) AS primary_phone,
    (SELECT ce.email_address FROM contact_emails ce WHERE ce.contact_id = c.id AND ce.is_primary = TRUE LIMIT 1) AS primary_email,
    -- Order stats
    (SELECT COUNT(*) FROM orders o WHERE o.contact_id = c.id AND o.is_active = TRUE) AS total_orders,
    (SELECT COALESCE(SUM(o.total), 0) FROM orders o WHERE o.contact_id = c.id AND o.is_active = TRUE) AS lifetime_value,
    (SELECT MAX(o.order_date) FROM orders o WHERE o.contact_id = c.id AND o.is_active = TRUE) AS last_order_date,
    -- Communication stats
    (SELECT COUNT(*) FROM communications cm WHERE cm.contact_id = c.id) AS total_communications,
    (SELECT MAX(cm.occurred_at) FROM communications cm WHERE cm.contact_id = c.id) AS last_communication_at,
    -- Invoice stats
    (SELECT COALESCE(SUM(i.balance_due), 0)
     FROM invoices i
     JOIN orders o ON i.order_id = o.id
     WHERE o.contact_id = c.id AND i.is_active = TRUE) AS outstanding_balance,
    -- Marketing sources
    (SELECT GROUP_CONCAT(ms.label ORDER BY ms.sort_order SEPARATOR ', ')
     FROM contact_marketing_sources cms
     JOIN marketing_sources ms ON cms.marketing_source_id = ms.id
     WHERE cms.contact_id = c.id) AS marketing_sources,
    -- Tags
    (SELECT GROUP_CONCAT(t.label ORDER BY t.sort_order SEPARATOR ', ')
     FROM contact_tag_map ctm
     JOIN tags t ON ctm.tag_id = t.id
     WHERE ctm.contact_id = c.id) AS tags
FROM contacts c
JOIN contact_types ct ON c.contact_type_id = ct.id
LEFT JOIN organizations org ON c.organization_id = org.id;
