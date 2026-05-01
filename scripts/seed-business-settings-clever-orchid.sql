-- One-shot: seed the business_settings singleton on the
-- Clever Orchid VPS. Pre-v0.3.3 installs left the table
-- empty; this is the CO-specific row, committed for audit.
--
-- Run once on CO only:
--
--   ssh root@165.245.130.39 \
--     'docker exec -i clienthub-mariadb mariadb -uroot -p"$PW" clienthub' \
--     < scripts/seed-business-settings-clever-orchid.sql
--
-- Idempotent guard: only inserts when the table is currently empty,
-- so re-running on a populated table is a no-op.

INSERT INTO business_settings
    (business_name, business_type, timezone, currency, country,
     phone, email, website)
SELECT
    'Clever Orchid',
    'embroidery',
    'America/New_York',
    'USD',
    'US',
    NULL,
    NULL,
    'https://cleverorchid.com'
WHERE NOT EXISTS (SELECT 1 FROM business_settings);
