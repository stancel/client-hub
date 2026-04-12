-- Migration 010: Communications log
-- Depends on: contacts, channel_types, orders

CREATE TABLE IF NOT EXISTS communications (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    contact_id BIGINT UNSIGNED NOT NULL,
    channel_type_id BIGINT UNSIGNED NOT NULL,
    order_id BIGINT UNSIGNED NULL,
    direction ENUM('inbound','outbound') NOT NULL,
    subject VARCHAR(255) NULL,
    body TEXT NULL,
    occurred_at DATETIME NOT NULL,
    external_message_id VARCHAR(255) NULL,
    created_by VARCHAR(100) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY idx_comm_uuid (uuid),
    KEY idx_comm_contact (contact_id),
    KEY idx_comm_channel (channel_type_id),
    KEY idx_comm_order (order_id),
    KEY idx_comm_occurred (occurred_at),
    KEY idx_comm_external (external_message_id),
    CONSTRAINT fk_comm_contact FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    CONSTRAINT fk_comm_channel FOREIGN KEY (channel_type_id) REFERENCES channel_types(id),
    CONSTRAINT fk_comm_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
