-- Backfill: replace docker-network IP key_values in spam_rate_log
-- with the real client IP from the contemporaneous contact's
-- external_refs_json (matched by occurred_at within ±2 seconds of
-- contact.created_at).
--
-- Run once on each instance after the 025 schema migration has been
-- applied AND the new uvicorn --proxy-headers configuration has been
-- redeployed. See docs/Spam-Defense-Pattern.rst.
--
--   Cybertron dev (local):
--     docker exec mariadb mariadb -uroot -p clienthub \
--       < scripts/backfill-spam-rate-log-ip.sql
--
--   Production VPS (CDC / Clever Orchid / etc.):
--     docker exec clienthub-mariadb mariadb -uroot -p"$ROOT_PW" clienthub \
--       < scripts/backfill-spam-rate-log-ip.sql
--
-- Idempotent: re-running it is a no-op once values are real public IPs.

-- Pass 1 — fix matched docker-network rows from the contact's external_refs.
UPDATE spam_rate_log srl
JOIN contacts c
  ON ABS(TIMESTAMPDIFF(SECOND, c.created_at, srl.occurred_at)) <= 2
SET srl.key_value = JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.ip_address'))
WHERE srl.key_type = 'ip'
  AND (
       srl.key_value LIKE '172.16.%'
    OR srl.key_value LIKE '172.17.%'
    OR srl.key_value LIKE '172.18.%'
    OR srl.key_value LIKE '172.19.%'
    OR srl.key_value LIKE '172.20.%'
    OR srl.key_value LIKE '172.21.%'
    OR srl.key_value LIKE '172.22.%'
    OR srl.key_value LIKE '172.23.%'
    OR srl.key_value LIKE '172.24.%'
    OR srl.key_value LIKE '172.25.%'
    OR srl.key_value LIKE '172.26.%'
    OR srl.key_value LIKE '172.27.%'
    OR srl.key_value LIKE '172.28.%'
    OR srl.key_value LIKE '172.29.%'
    OR srl.key_value LIKE '172.30.%'
    OR srl.key_value LIKE '172.31.%'
  )
  AND JSON_EXTRACT(c.external_refs_json, '$.ip_address') IS NOT NULL;

-- Pass 2 — anything still on a private docker IP couldn't be matched to a
-- contemporaneous contact (could be a webhook submission). Mark it so it's
-- obvious in the admin UI / queries. Prefixed value is not a valid IP-key,
-- and rate-limit lookups won't false-match against it.
UPDATE spam_rate_log
SET key_value = CONCAT('unresolved:', key_value)
WHERE key_type = 'ip'
  AND (
       key_value LIKE '172.1[6-9].%'
    OR key_value LIKE '172.2_.%'
    OR key_value LIKE '172.3[0-1].%'
    OR key_value LIKE '10.%'
    OR key_value LIKE '192.168.%'
    OR key_value = '127.0.0.1'
  )
  AND key_value NOT LIKE 'unresolved:%';

-- Sanity check (run after to verify):
-- SELECT key_type, key_value, COUNT(*) AS n
--   FROM spam_rate_log
--  WHERE key_type='ip'
--  GROUP BY key_value
--  ORDER BY n DESC;
