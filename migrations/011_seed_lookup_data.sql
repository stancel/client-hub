-- Migration 011: Seed lookup tables with reference data

-- Contact Types
INSERT IGNORE INTO contact_types (code, label, description, sort_order) VALUES
('client', 'Client', 'Confirmed customer who has done business with us', 1),
('prospect', 'Prospect', 'Potential customer who has not yet converted', 2),
('lead', 'Lead', 'Initial contact, not yet qualified', 3),
('vendor', 'Vendor', 'Supplier or service provider', 4),
('other', 'Other', 'Other contact type', 99);

-- Phone Types
INSERT IGNORE INTO phone_types (code, label, sort_order) VALUES
('mobile', 'Mobile', 1),
('home', 'Home', 2),
('work', 'Work', 3),
('fax', 'Fax', 4),
('other', 'Other', 99);

-- Email Types
INSERT IGNORE INTO email_types (code, label, sort_order) VALUES
('personal', 'Personal', 1),
('work', 'Work', 2),
('billing', 'Billing', 3),
('other', 'Other', 99);

-- Address Types
INSERT IGNORE INTO address_types (code, label, sort_order) VALUES
('home', 'Home', 1),
('work', 'Work', 2),
('billing', 'Billing', 3),
('shipping', 'Shipping', 4),
('other', 'Other', 99);

-- Channel Types
INSERT IGNORE INTO channel_types (code, label, description, sort_order) VALUES
('sms', 'SMS/MMS', 'Text messaging', 1),
('email', 'Email', 'Email communication', 2),
('phone', 'Phone Call', 'Voice phone call', 3),
('chat', 'Website Chat', 'Website chatbot or live chat', 4),
('portal', 'Online Portal', 'Customer self-service portal', 5),
('in_person', 'In Person', 'Face-to-face interaction', 6);

-- Marketing Sources
INSERT IGNORE INTO marketing_sources (code, label, description, sort_order) VALUES
('google_search', 'Google Search', 'Found via Google organic search', 1),
('social_media_ad', 'Social Media Ad', 'Paid social media advertisement', 2),
('social_media_organic', 'Social Media (Organic)', 'Organic social media discovery', 3),
('referral', 'Referral', 'Referred by another customer or contact', 4),
('walk_in', 'Walk-In', 'Walked into physical location', 5),
('phone_call', 'Phone Call', 'Called us directly', 6),
('website', 'Website', 'Found via website (non-search)', 7),
('word_of_mouth', 'Word of Mouth', 'Heard about us from someone', 8),
('repeat', 'Repeat Customer', 'Returning customer', 9),
('other', 'Other', 'Other marketing source', 99);

-- Order Statuses
INSERT IGNORE INTO order_statuses (code, label, description, sort_order) VALUES
('quoted', 'Quoted', 'Quote provided, awaiting confirmation', 1),
('confirmed', 'Confirmed', 'Order confirmed by customer', 2),
('in_progress', 'In Progress', 'Work is underway', 3),
('completed', 'Completed', 'Order fulfilled and delivered', 4),
('cancelled', 'Cancelled', 'Order cancelled', 5),
('on_hold', 'On Hold', 'Order temporarily paused', 6);

-- Order Item Types
INSERT IGNORE INTO order_item_types (code, label, description, sort_order) VALUES
('product', 'Product', 'Physical or digital product', 1),
('service', 'Service', 'Service performed', 2),
('booking', 'Booking', 'Appointment or reservation', 3),
('other', 'Other', 'Other item type', 99);

-- Invoice Statuses
INSERT IGNORE INTO invoice_statuses (code, label, description, sort_order) VALUES
('draft', 'Draft', 'Invoice not yet sent', 1),
('sent', 'Sent', 'Invoice sent to customer', 2),
('paid', 'Paid', 'Invoice fully paid', 3),
('partial', 'Partially Paid', 'Invoice partially paid', 4),
('overdue', 'Overdue', 'Invoice past due date', 5),
('void', 'Void', 'Invoice voided/cancelled', 6);

-- Payment Methods
INSERT IGNORE INTO payment_methods (code, label, sort_order) VALUES
('cash', 'Cash', 1),
('credit_card', 'Credit Card', 2),
('debit_card', 'Debit Card', 3),
('check', 'Check', 4),
('bank_transfer', 'Bank Transfer', 5),
('online', 'Online Payment', 6),
('other', 'Other', 99);
