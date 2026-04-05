-- Migration 007: Contact channel preferences, marketing sources, tags, notes
-- Depends on: contacts, channel_types, marketing_sources, tags

CREATE TABLE contact_channel_prefs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    contact_id BIGINT UNSIGNED NOT NULL,
    channel_type_id BIGINT UNSIGNED NOT NULL,
    is_preferred BOOLEAN NOT NULL DEFAULT FALSE,
    opt_in_status ENUM('opted_in','opted_out','not_set') NOT NULL DEFAULT 'not_set',
    opted_in_at DATETIME NULL,
    opted_out_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_ccp_contact_channel (contact_id, channel_type_id),
    CONSTRAINT fk_ccp_contact FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    CONSTRAINT fk_ccp_channel FOREIGN KEY (channel_type_id) REFERENCES channel_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE contact_marketing_sources (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    contact_id BIGINT UNSIGNED NOT NULL,
    marketing_source_id BIGINT UNSIGNED NOT NULL,
    source_detail VARCHAR(255) NULL,
    attributed_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_cms_contact_source (contact_id, marketing_source_id),
    KEY idx_cms_contact (contact_id),
    KEY idx_cms_source (marketing_source_id),
    CONSTRAINT fk_cms_contact FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    CONSTRAINT fk_cms_source FOREIGN KEY (marketing_source_id) REFERENCES marketing_sources(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE contact_tag_map (
    contact_id BIGINT UNSIGNED NOT NULL,
    tag_id BIGINT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, tag_id),
    CONSTRAINT fk_ctm_contact FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    CONSTRAINT fk_ctm_tag FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE contact_notes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    contact_id BIGINT UNSIGNED NOT NULL,
    note_text TEXT NOT NULL,
    created_by VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_cn_contact (contact_id),
    CONSTRAINT fk_cn_contact FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
