-- Migration 002: Business Settings (singleton config table)

CREATE TABLE business_settings (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100) NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/Chicago',
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    tax_rate DECIMAL(5,4) NULL,
    phone VARCHAR(20) NULL,
    email VARCHAR(255) NULL,
    website VARCHAR(255) NULL,
    address_line1 VARCHAR(255) NULL,
    address_line2 VARCHAR(255) NULL,
    city VARCHAR(100) NULL,
    state VARCHAR(50) NULL,
    postal_code VARCHAR(20) NULL,
    country CHAR(2) NOT NULL DEFAULT 'US',
    settings_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
