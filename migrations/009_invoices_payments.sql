-- Migration 009: Invoices and payments
-- Depends on: orders, invoice_statuses, payment_methods

CREATE TABLE IF NOT EXISTS invoices (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    order_id BIGINT UNSIGNED NOT NULL,
    invoice_status_id BIGINT UNSIGNED NOT NULL,
    invoice_number VARCHAR(50) NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NULL,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    amount_paid DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    balance_due DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    external_invoice_id VARCHAR(255) NULL,
    notes_text TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_inv_uuid (uuid),
    UNIQUE KEY idx_inv_number (invoice_number),
    KEY idx_inv_order (order_id),
    KEY idx_inv_status (invoice_status_id),
    KEY idx_inv_external (external_invoice_id),
    CONSTRAINT fk_inv_order FOREIGN KEY (order_id) REFERENCES orders(id),
    CONSTRAINT fk_inv_status FOREIGN KEY (invoice_status_id) REFERENCES invoice_statuses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    invoice_id BIGINT UNSIGNED NOT NULL,
    payment_method_id BIGINT UNSIGNED NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_date DATE NOT NULL,
    reference_number VARCHAR(255) NULL,
    external_payment_id VARCHAR(255) NULL,
    notes_text TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_pay_uuid (uuid),
    KEY idx_pay_invoice (invoice_id),
    KEY idx_pay_date (payment_date),
    KEY idx_pay_external (external_payment_id),
    CONSTRAINT fk_pay_invoice FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    CONSTRAINT fk_pay_method FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
