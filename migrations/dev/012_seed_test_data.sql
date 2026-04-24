-- Migration 012: Seed test data for validation
-- This data exercises all relationships, junction tables, and integration use cases.
-- Use for development/testing only — do NOT run in production.

-- Business settings (embroidery business)
INSERT IGNORE INTO business_settings (business_name, business_type, timezone, currency, tax_rate, phone, email, website, address_line1, city, state, postal_code, country)
VALUES ('Stitch & Style Embroidery', 'embroidery', 'America/Chicago', 'USD', 0.0825, '555-555-0100', 'info@stitchandstyle.example.com', 'https://stitchandstyle.example.com', '123 Main Street', 'Dallas', 'TX', '75201', 'US');

-- Organizations
INSERT IGNORE INTO organizations (uuid, name, org_type, website, created_by) VALUES
(UUID(), 'Dallas Dental Group', 'company', 'https://dallasdental.example.com', 'system'),
(UUID(), 'Smith Household', 'household', NULL, 'system');

-- Tags
INSERT IGNORE INTO tags (code, label, sort_order) VALUES
('vip', 'VIP Customer', 1),
('repeat', 'Repeat Customer', 2),
('referral_source', 'Referral Source', 3);

-- Contacts (5 total: 2 clients, 1 prospect, 1 lead, 1 vendor)
-- (Migration 021 dropped contacts.organization_id — organization
--  links now live in contact_org_affiliations; see affiliation
--  INSERT below.)
INSERT IGNORE INTO contacts (uuid, contact_type_id, first_name, last_name, display_name, enrichment_status, external_refs_json, created_by)
VALUES (UUID(), 1, 'Sarah', 'Johnson', NULL, 'complete', '{"invoiceninja": "INV-C-001", "chatwoot": "CW-1001"}', 'system');

INSERT IGNORE INTO contacts (uuid, contact_type_id, first_name, last_name, enrichment_status, created_by)
VALUES (UUID(), 2, 'Dr. Michael', 'Chen', 'partial', 'system');

-- Affiliation: Dr. Michael Chen (contact 2) is primary at Dallas Dental Group (org 1)
INSERT IGNORE INTO contact_org_affiliations (uuid, contact_id, organization_id, role_title, is_primary, is_active, created_by)
VALUES (UUID(), 2, 1, 'Lead Dentist', TRUE, TRUE, 'system');

INSERT IGNORE INTO contacts (uuid, contact_type_id, first_name, last_name, enrichment_status, created_by)
VALUES (UUID(), 3, 'Emily', 'Rodriguez', 'needs_review', 'website_form');

INSERT IGNORE INTO contacts (uuid, contact_type_id, first_name, last_name, converted_at, converted_from_type_id, enrichment_status, created_by)
VALUES (UUID(), 1, 'James', 'Smith', '2026-03-15 10:30:00', 2, 'complete', 'system');

INSERT IGNORE INTO contacts (uuid, contact_type_id, first_name, last_name, enrichment_status, notes_text, created_by)
VALUES (UUID(), 4, 'Thread', 'Supply Co', 'complete', 'Primary thread and fabric supplier', 'system');

-- Phone numbers (multiple per contact, testing CTI lookup)
INSERT IGNORE INTO contact_phones (contact_id, phone_type_id, phone_number, is_primary, is_verified, verified_at, data_source) VALUES
(1, 1, '+15555550101', TRUE, TRUE, '2026-01-15 09:00:00', 'manual'),
(1, 3, '+15555550102', FALSE, FALSE, NULL, 'invoiceninja'),
(2, 3, '+15555550201', TRUE, FALSE, NULL, 'manual'),
(3, 1, '+15555550301', TRUE, FALSE, NULL, 'website_form'),
(4, 1, '+15555550401', TRUE, TRUE, '2026-03-15 10:30:00', 'manual'),
(4, 2, '+15555550402', FALSE, FALSE, NULL, 'enrichment');
UPDATE contact_phones SET is_enriched = TRUE WHERE phone_number = '+15555550402';

-- Email addresses
INSERT IGNORE INTO contact_emails (contact_id, email_type_id, email_address, is_primary, is_verified, verified_at, data_source) VALUES
(1, 1, 'sarah.johnson@example.com', TRUE, TRUE, '2026-01-15 09:00:00', 'manual'),
(1, 3, 'sarah.billing@example.com', FALSE, FALSE, NULL, 'invoiceninja'),
(2, 2, 'dr.chen@dallasdental.example.com', TRUE, FALSE, NULL, 'manual'),
(3, 1, 'emily.r@example.com', TRUE, FALSE, NULL, 'website_form'),
(4, 1, 'james.smith@example.com', TRUE, TRUE, '2026-03-15 10:30:00', 'manual');

-- Physical addresses
INSERT IGNORE INTO contact_addresses (contact_id, address_type_id, address_line1, city, state, postal_code, country, is_primary, data_source) VALUES
(1, 1, '456 Oak Lane', 'Dallas', 'TX', '75201', 'US', TRUE, 'manual'),
(1, 4, '789 Shipping Blvd', 'Dallas', 'TX', '75202', 'US', FALSE, 'manual'),
(4, 1, '321 Elm Street', 'Plano', 'TX', '75023', 'US', TRUE, 'manual');

-- Organization details
INSERT IGNORE INTO org_phones (organization_id, phone_type_id, phone_number, is_primary, data_source) VALUES (1, 3, '+15555550500', TRUE, 'manual');
INSERT IGNORE INTO org_emails (organization_id, email_type_id, email_address, is_primary, data_source) VALUES (1, 2, 'office@dallasdental.example.com', TRUE, 'manual');
INSERT IGNORE INTO org_addresses (organization_id, address_type_id, address_line1, city, state, postal_code, country, is_primary, data_source) VALUES (1, 2, '100 Medical Plaza Dr', 'Dallas', 'TX', '75230', 'US', TRUE, 'manual');

-- Channel preferences
INSERT IGNORE INTO contact_channel_prefs (contact_id, channel_type_id, is_preferred, opt_in_status, opted_in_at) VALUES
(1, 1, TRUE, 'opted_in', '2026-01-15 09:00:00'),
(1, 2, FALSE, 'opted_in', '2026-01-15 09:00:00'),
(1, 3, FALSE, 'opted_out', NULL),
(2, 2, TRUE, 'opted_in', '2026-02-01 14:00:00'),
(3, 4, TRUE, 'not_set', NULL),
(4, 1, TRUE, 'opted_in', '2026-03-15 10:30:00');

-- Marketing sources (M:M junction)
INSERT IGNORE INTO contact_marketing_sources (contact_id, marketing_source_id, source_detail, attributed_at) VALUES
(1, 1, 'Searched "custom embroidery Dallas TX"', '2025-12-20 00:00:00'),
(1, 4, 'Referred by James Smith', '2025-12-22 00:00:00'),
(2, 6, 'Called to inquire about staff uniforms', '2026-02-01 14:00:00'),
(3, 7, 'Visited website from Instagram link', '2026-03-28 00:00:00'),
(3, 2, 'Clicked Instagram ad for monogramming', '2026-03-28 00:00:00'),
(4, 8, 'Heard about us from a friend', '2026-01-10 00:00:00');

-- Tags (M:M junction)
INSERT IGNORE INTO contact_tag_map (contact_id, tag_id) VALUES (1, 1), (1, 2), (4, 2), (4, 3);

-- Orders
INSERT IGNORE INTO orders (uuid, contact_id, order_status_id, order_number, order_date, due_date, subtotal, discount_amount, tax_amount, total, created_by)
VALUES (UUID(), 1, 4, 'ORD-2026-001', '2026-01-20', '2026-02-03', 150.00, 0.00, 12.38, 162.38, 'system');
INSERT IGNORE INTO orders (uuid, contact_id, order_status_id, order_number, order_date, due_date, subtotal, discount_amount, tax_amount, total, notes_text, created_by)
VALUES (UUID(), 1, 3, 'ORD-2026-002', '2026-03-25', '2026-04-10', 275.00, 25.00, 20.63, 270.63, 'Rush order - customer needs by April 10', 'system');
INSERT IGNORE INTO orders (uuid, contact_id, order_status_id, order_number, order_date, subtotal, tax_amount, total, notes_text, created_by)
VALUES (UUID(), 2, 1, 'ORD-2026-003', '2026-04-01', 1200.00, 99.00, 1299.00, 'Bulk order: 50 lab coats with practice logo', 'system');
INSERT IGNORE INTO orders (uuid, contact_id, order_status_id, order_number, order_date, due_date, scheduled_at, subtotal, tax_amount, total, created_by)
VALUES (UUID(), 4, 4, 'ORD-2026-004', '2026-03-15', '2026-03-20', '2026-03-18 14:00:00', 85.00, 7.01, 92.01, 'system');

-- Order items
INSERT IGNORE INTO order_items (order_id, item_type_id, description, quantity, unit_price, discount_amount, line_total, sort_order) VALUES
(1, 1, 'Custom embroidered polo shirts', 5.00, 30.00, 0.00, 150.00, 1),
(2, 1, 'Monogrammed towel set - bath', 10.00, 20.00, 0.00, 200.00, 1),
(2, 2, 'Rush processing fee', 1.00, 50.00, 0.00, 50.00, 2),
(2, 1, 'Gift wrapping', 10.00, 2.50, 0.00, 25.00, 3),
(3, 1, 'Lab coat with embroidered logo', 50.00, 24.00, 0.00, 1200.00, 1),
(4, 2, 'Custom patch design consultation', 1.00, 35.00, 0.00, 35.00, 1),
(4, 1, 'Iron-on custom patches (set of 10)', 1.00, 50.00, 0.00, 50.00, 2);

-- Order status history
INSERT IGNORE INTO order_status_history (order_id, from_status_id, to_status_id, changed_by, created_at) VALUES
(1, NULL, 1, 'system', '2026-01-20 09:00:00'), (1, 1, 2, 'system', '2026-01-20 10:00:00'),
(1, 2, 3, 'system', '2026-01-25 08:00:00'), (1, 3, 4, 'system', '2026-02-02 16:00:00'),
(2, NULL, 2, 'system', '2026-03-25 11:00:00'), (2, 2, 3, 'system', '2026-03-26 09:00:00'),
(3, NULL, 1, 'system', '2026-04-01 14:00:00'),
(4, NULL, 2, 'system', '2026-03-15 10:30:00'), (4, 2, 3, 'system', '2026-03-18 14:00:00'),
(4, 3, 4, 'system', '2026-03-20 11:00:00');

-- Invoices
INSERT IGNORE INTO invoices (uuid, order_id, invoice_status_id, invoice_number, invoice_date, due_date, subtotal, tax_amount, total, amount_paid, balance_due, external_invoice_id)
VALUES (UUID(), 1, 3, 'INV-2026-001', '2026-01-20', '2026-02-03', 150.00, 12.38, 162.38, 162.38, 0.00, 'NINJA-INV-10001');
INSERT IGNORE INTO invoices (uuid, order_id, invoice_status_id, invoice_number, invoice_date, due_date, subtotal, tax_amount, total, amount_paid, balance_due)
VALUES (UUID(), 2, 4, 'INV-2026-002', '2026-03-25', '2026-04-10', 137.50, 10.31, 147.81, 100.00, 47.81);
INSERT IGNORE INTO invoices (uuid, order_id, invoice_status_id, invoice_number, invoice_date, due_date, subtotal, tax_amount, total, amount_paid, balance_due, external_invoice_id)
VALUES (UUID(), 4, 3, 'INV-2026-003', '2026-03-15', '2026-03-20', 85.00, 7.01, 92.01, 92.01, 0.00, 'NINJA-INV-10002');

-- Payments
INSERT IGNORE INTO payments (uuid, invoice_id, payment_method_id, amount, payment_date, reference_number, external_payment_id) VALUES
(UUID(), 1, 2, 162.38, '2026-02-01', 'VISA-****-4532', 'NINJA-PAY-20001'),
(UUID(), 2, 6, 100.00, '2026-03-25', 'ONLINE-TXN-78901', NULL),
(UUID(), 3, 1, 92.01, '2026-03-18', NULL, 'NINJA-PAY-20002');

-- Communications
INSERT IGNORE INTO communications (uuid, contact_id, channel_type_id, order_id, direction, subject, body, occurred_at, external_message_id, created_by) VALUES
(UUID(), 1, 1, NULL, 'inbound', NULL, 'Hi, I saw your embroidery work online. Do you do custom polo shirts?', '2025-12-20 14:30:00', 'CW-MSG-1001', 'chatwoot'),
(UUID(), 1, 1, NULL, 'outbound', NULL, 'Yes we do! Would you like to come in for a consultation?', '2025-12-20 14:35:00', 'CW-MSG-1002', 'chatwoot'),
(UUID(), 1, 3, 1, 'inbound', 'Order pickup confirmation', NULL, '2026-02-02 15:00:00', NULL, 'system'),
(UUID(), 2, 3, NULL, 'inbound', 'Inquiry about bulk lab coat embroidery', NULL, '2026-02-01 14:00:00', NULL, 'manual'),
(UUID(), 2, 2, 3, 'outbound', 'Quote for 50 embroidered lab coats', 'Dear Dr. Chen, please find attached our quote...', '2026-04-01 15:00:00', NULL, 'system'),
(UUID(), 3, 4, NULL, 'inbound', 'Website chat inquiry', 'Looking for monogrammed gifts for a wedding party', '2026-03-28 11:00:00', 'CW-MSG-2001', 'chatwoot'),
(UUID(), 4, 1, 4, 'outbound', NULL, 'Hi James, your custom patches are ready for pickup!', '2026-03-20 10:00:00', 'CW-MSG-3001', 'chatwoot');

-- Contact notes
INSERT IGNORE INTO contact_notes (contact_id, note_text, created_by) VALUES
(1, 'Sarah is a fantastic repeat customer. Always refers friends. Give her 10% loyalty discount on next order.', 'brad'),
(2, 'Dr. Chen is interested in outfitting entire dental staff. High-value prospect. Follow up by April 15.', 'brad'),
(3, 'Emily found us through Instagram ad. Interested in wedding party gifts. Needs follow-up with options catalog.', 'website_form');
