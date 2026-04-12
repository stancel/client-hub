-- Migration 003: Organizations
-- Must be created before contacts (contacts.organization_id references this)

CREATE TABLE IF NOT EXISTS organizations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(100) NULL,
    website VARCHAR(255) NULL,
    notes_text TEXT NULL,
    external_refs_json JSON NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    UNIQUE KEY idx_orgs_uuid (uuid),
    KEY idx_orgs_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
