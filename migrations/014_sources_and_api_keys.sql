-- Migration 014: Sources and API Keys tables
-- Sources = which system/integration logged the event (website, cti, chatwoot, etc.)
-- DISTINCT from marketing_sources = where the lead discovered the business (google, referral, etc.)

CREATE TABLE sources (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(32) NOT NULL DEFAULT 'website',
    domain VARCHAR(255) NULL,
    description TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_sources_uuid (uuid),
    KEY idx_sources_active (is_active),
    KEY idx_sources_type (source_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE api_keys (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    source_id BIGINT UNSIGNED NOT NULL,
    key_prefix VARCHAR(16) NOT NULL,
    key_value VARCHAR(128) NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME NULL,
    revoked_at DATETIME NULL,
    UNIQUE KEY idx_api_keys_uuid (uuid),
    UNIQUE KEY idx_api_keys_value (key_value),
    KEY idx_api_keys_source (source_id),
    KEY idx_api_keys_prefix (key_prefix),
    KEY idx_api_keys_active (is_active),
    CONSTRAINT fk_api_keys_source FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed bootstrap source for existing data and fresh installs
INSERT INTO sources (uuid, code, name, source_type, description, is_active)
VALUES (UUID(), 'bootstrap', 'Bootstrap Source', 'other',
        'Initial source created by the installer. Rename or create additional sources as needed.',
        TRUE);
