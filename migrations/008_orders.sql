-- Migration 008: Orders, order items, order status history
-- Depends on: contacts, order_statuses, order_item_types

CREATE TABLE orders (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    contact_id BIGINT UNSIGNED NOT NULL,
    order_status_id BIGINT UNSIGNED NOT NULL,
    order_number VARCHAR(50) NULL,
    order_date DATE NOT NULL,
    due_date DATE NULL,
    scheduled_at DATETIME NULL,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    notes_text TEXT NULL,
    external_refs_json JSON NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    UNIQUE KEY idx_orders_uuid (uuid),
    UNIQUE KEY idx_orders_number (order_number),
    KEY idx_orders_contact (contact_id),
    KEY idx_orders_status (order_status_id),
    KEY idx_orders_date (order_date),
    KEY idx_orders_scheduled (scheduled_at),
    CONSTRAINT fk_orders_contact FOREIGN KEY (contact_id) REFERENCES contacts(id),
    CONSTRAINT fk_orders_status FOREIGN KEY (order_status_id) REFERENCES order_statuses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE order_items (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT UNSIGNED NOT NULL,
    item_type_id BIGINT UNSIGNED NOT NULL,
    description VARCHAR(500) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL DEFAULT 1.00,
    unit_price DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    line_total DECIMAL(12,2) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    notes_text TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_oi_order (order_id),
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_oi_item_type FOREIGN KEY (item_type_id) REFERENCES order_item_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE order_status_history (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT UNSIGNED NOT NULL,
    from_status_id BIGINT UNSIGNED NULL,
    to_status_id BIGINT UNSIGNED NOT NULL,
    changed_by VARCHAR(100) NULL,
    notes_text TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_osh_order (order_id),
    KEY idx_osh_date (created_at),
    CONSTRAINT fk_osh_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_osh_from FOREIGN KEY (from_status_id) REFERENCES order_statuses(id),
    CONSTRAINT fk_osh_to FOREIGN KEY (to_status_id) REFERENCES order_statuses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
