-- Migration 016: Cross-project Web Factory channel types
-- These are the canonical event codes every Web Factory site uses.

INSERT INTO channel_types (code, label, description, sort_order) VALUES
  ('web_form',            'Web Form',            'Contact form submission from a website',                   10),
  ('appointment_request', 'Appointment Request', 'Online appointment request (pre-scheduler)',               11),
  ('booking_started',     'Booking Started',     'User started the booking flow',                            12),
  ('booking_completed',   'Booking Completed',   'Appointment booking confirmed',                            13),
  ('booking_cancelled',   'Booking Cancelled',   'Appointment cancelled after booking',                      14),
  ('phone_click',         'Phone Click',         'User clicked a tel: link on a website',                    15),
  ('book_click',          'Book Click',          'User clicked a CTA linking to the booking page',           16),
  ('form_submit',         'Form Submit',         'Generic form submission (fallback when no specific type)',  17),
  ('scroll_depth',        'Scroll Depth',        'User scrolled past a tracked milestone (50/75/90)',        18),
  ('page_view',           'Page View',           'High-intent page view (service page, pricing page)',       19);
