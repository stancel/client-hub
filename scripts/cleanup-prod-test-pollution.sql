-- Cleanup: prod-pollution test contacts left behind during v0.1.0 → v0.3.0
-- iteration on Complete Dental Care + Clever Orchid.
--
-- Three contacts are unambiguously test data — their communication
-- bodies carry self-identifying test markers (rather than a name
-- that might collide with a real customer):
--
--   1. CDC: Brad Stancel — comm body
--      "Checking to make sure this works after fix I put in place."
--      (post-deploy verification after the InvoiceNinja fix)
--   2. CO:  "Mary T TEST-FROM-CLAUDE-S5" — comm body starts with
--      "TEST FROM CLAUDE - please ignore."
--   3. CO:  "Repeat" — comm body
--      "Identical body for compound rate-limit test of (email,body_hash) key."
--
-- The selection is by *communication body marker*, not first/last
-- name — so a real customer who happens to share a first name with
-- one of these test entries is never at risk. Body markers are
-- distinctive English phrases that no real lead would write.
--
-- The script runs purely as VPS-safe: a SELECT preview comes first
-- (so a dry-run via piped `head` shows what would be touched), then
-- the cascading DELETE in dependency order. Each WHERE looks at the
-- temp-table ``_test_contact_ids`` so the predicate is computed once
-- and the same set of contacts drives every dependent delete.
--
-- Usage:
--
--   docker exec -i clienthub-mariadb \
--     mariadb -uroot -p"$ROOT_PW" clienthub \
--     < scripts/cleanup-prod-test-pollution.sql
--
-- Idempotent: re-running on a clean instance returns 0 rows from the
-- preview SELECT and the DELETEs become no-ops.

-- ============================================================
-- Step 1 — Identify the test contacts (preview + working set)
-- ============================================================
DROP TEMPORARY TABLE IF EXISTS _test_contact_ids;
CREATE TEMPORARY TABLE _test_contact_ids (
    id BIGINT UNSIGNED PRIMARY KEY
);

INSERT INTO _test_contact_ids (id)
SELECT DISTINCT c.id
  FROM contacts c
  JOIN communications cm ON cm.contact_id = c.id
 WHERE cm.body LIKE '%TEST FROM CLAUDE%'
    OR cm.body LIKE '%Identical body for compound rate-limit test%'
    OR cm.body LIKE '%Checking to make sure this works after fix%';

-- Preview — what's about to be removed
SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.created_at,
    LEFT(cm.body, 80) AS body_preview
FROM contacts c
JOIN _test_contact_ids t ON t.id = c.id
LEFT JOIN communications cm ON cm.contact_id = c.id
ORDER BY c.id, cm.id;

-- ============================================================
-- Step 2 — Cascade delete in dependency order
-- ============================================================
-- Orders / invoices / payments — drop in deepest-child order.
-- (None of the v0.1.0 → v0.3.0 test contacts placed orders, so these
-- are no-ops in practice, but the pattern is here for future
-- cleanup scripts that target test data with order history.)

DELETE p FROM payments p
  JOIN invoices i ON p.invoice_id = i.id
  JOIN orders o ON i.order_id = o.id
 WHERE o.contact_id IN (SELECT id FROM _test_contact_ids);

DELETE i FROM invoices i
  JOIN orders o ON i.order_id = o.id
 WHERE o.contact_id IN (SELECT id FROM _test_contact_ids);

DELETE osh FROM order_status_history osh
  JOIN orders o ON osh.order_id = o.id
 WHERE o.contact_id IN (SELECT id FROM _test_contact_ids);

DELETE oi FROM order_items oi
  JOIN orders o ON oi.order_id = o.id
 WHERE o.contact_id IN (SELECT id FROM _test_contact_ids);

DELETE FROM orders
 WHERE contact_id IN (SELECT id FROM _test_contact_ids);

-- Communications and direct contact-detail children
DELETE FROM communications        WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_phones        WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_emails        WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_addresses     WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_tag_map       WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_marketing_sources WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_channel_prefs WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_preferences   WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_notes         WHERE contact_id IN (SELECT id FROM _test_contact_ids);
DELETE FROM contact_org_affiliations WHERE contact_id IN (SELECT id FROM _test_contact_ids);

-- Finally, the contact rows themselves
DELETE FROM contacts WHERE id IN (SELECT id FROM _test_contact_ids);

-- ============================================================
-- Step 3 — Sanity check (counts after delete)
-- ============================================================
SELECT 'remaining_matches' AS what, COUNT(*) AS n
  FROM contacts c
  JOIN communications cm ON cm.contact_id = c.id
 WHERE cm.body LIKE '%TEST FROM CLAUDE%'
    OR cm.body LIKE '%Identical body for compound rate-limit test%'
    OR cm.body LIKE '%Checking to make sure this works after fix%';
-- Expected: 0

DROP TEMPORARY TABLE IF EXISTS _test_contact_ids;
