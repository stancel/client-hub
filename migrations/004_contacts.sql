-- Migration 004: Contacts (central entity)
-- Depends on: contact_types, organizations

CREATE TABLE contacts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    contact_type_id BIGINT UNSIGNED NOT NULL,
    organization_id BIGINT UNSIGNED NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NULL,
    date_of_birth DATE NULL,
    converted_at DATETIME NULL,
    converted_from_type_id BIGINT UNSIGNED NULL,
    enrichment_status ENUM('complete','partial','needs_review') NOT NULL DEFAULT 'partial',
    notes_text TEXT NULL,
    external_refs_json JSON NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    UNIQUE KEY idx_contacts_uuid (uuid),
    KEY idx_contacts_type (contact_type_id),
    KEY idx_contacts_org (organization_id),
    KEY idx_contacts_name (last_name, first_name),
    KEY idx_contacts_enrichment (enrichment_status),
    KEY idx_contacts_active (is_active),
    CONSTRAINT fk_contacts_type FOREIGN KEY (contact_type_id) REFERENCES contact_types(id),
    CONSTRAINT fk_contacts_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    CONSTRAINT fk_contacts_converted_type FOREIGN KEY (converted_from_type_id) REFERENCES contact_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
