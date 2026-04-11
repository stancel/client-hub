#!/usr/bin/env bash
# cleanup-test-data.sh — Remove test/seed data from a Client Hub instance
#
# Dry-run by default. Use --apply to actually delete.
#
# Usage:
#   # Dry run (shows what would be deleted)
#   ./scripts/cleanup-test-data.sh --host 127.0.0.1 --password "$PASS"
#
#   # Apply for real
#   ./scripts/cleanup-test-data.sh --host 127.0.0.1 --password "$PASS" --apply
#
#   # Via docker compose on the VPS
#   docker compose -f docker-compose.bundled.yml exec -T mariadb \
#     mariadb -uroot -p"$PASS" clienthub < scripts/cleanup-test-data.sql

set -euo pipefail

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-clienthub}"
APPLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)     DB_HOST="$2"; shift 2 ;;
        --port)     DB_PORT="$2"; shift 2 ;;
        --user)     DB_USER="$2"; shift 2 ;;
        --password) DB_PASSWORD="$2"; shift 2 ;;
        --database) DB_NAME="$2"; shift 2 ;;
        --apply)    APPLY=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

MYSQL_CMD="mariadb -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USER}"
if [[ -n "$DB_PASSWORD" ]]; then
    MYSQL_CMD="$MYSQL_CMD -p${DB_PASSWORD}"
fi

echo "=== Client Hub Test Data Cleanup ==="
echo "Database: ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
echo "Mode: $(if $APPLY; then echo 'APPLY (will delete)'; else echo 'DRY RUN (preview only)'; fi)"
echo ""

# Build the WHERE clause for test contacts
TEST_CONTACTS_WHERE="(
    (first_name = 'Smoke' AND last_name = 'Test')
    OR last_name LIKE 'TestRun%'
    OR (first_name = 'Sarah' AND last_name = 'Johnson')
    OR (first_name = 'Emily' AND last_name = 'Rodriguez')
    OR (first_name = 'James' AND last_name = 'Smith')
    OR (first_name = 'Thread' AND last_name = 'Supply Co')
    OR (first_name = 'Dr. Michael' AND last_name = 'Chen')
    OR (first_name = 'E2E' AND last_name LIKE 'TestRun%')
)"

# Show what would be deleted
echo "Test contacts found:"
$MYSQL_CMD "$DB_NAME" -e "
SELECT id, first_name, last_name, created_at
FROM contacts
WHERE $TEST_CONTACTS_WHERE;
" 2>/dev/null

count=$($MYSQL_CMD "$DB_NAME" -N -e "
SELECT COUNT(*) FROM contacts WHERE $TEST_CONTACTS_WHERE;
" 2>/dev/null)

echo ""
echo "Total test contacts: $count"

if [[ "$count" -eq 0 ]]; then
    echo "No test data to clean up."
    exit 0
fi

if ! $APPLY; then
    echo ""
    echo "Dry run complete. Re-run with --apply to delete."
    exit 0
fi

echo ""
echo "Deleting test data..."

# Delete in dependency order (children first where CASCADE isn't set)
# Most child tables have ON DELETE CASCADE from contacts, but orders don't.
$MYSQL_CMD "$DB_NAME" -e "
SET @test_ids = NULL;
SELECT GROUP_CONCAT(id) INTO @test_ids FROM contacts WHERE $TEST_CONTACTS_WHERE;

-- Delete payments via invoices via orders
DELETE p FROM payments p
  JOIN invoices i ON p.invoice_id = i.id
  JOIN orders o ON i.order_id = o.id
  WHERE o.contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE i FROM invoices i
  JOIN orders o ON i.order_id = o.id
  WHERE o.contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE osh FROM order_status_history osh
  JOIN orders o ON osh.order_id = o.id
  WHERE o.contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE oi FROM order_items oi
  JOIN orders o ON oi.order_id = o.id
  WHERE o.contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM orders
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

-- Child tables with ON DELETE CASCADE will auto-delete, but be explicit
DELETE FROM communications
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_phones
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_emails
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_addresses
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_tag_map
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_marketing_sources
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_channel_prefs
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_preferences
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

DELETE FROM contact_notes
  WHERE contact_id IN (SELECT id FROM contacts WHERE $TEST_CONTACTS_WHERE);

-- Finally delete the contacts themselves
DELETE FROM contacts WHERE $TEST_CONTACTS_WHERE;

-- Also clean up test organizations
DELETE FROM org_phones WHERE organization_id IN (
  SELECT id FROM organizations WHERE name IN ('Dallas Dental Group', 'Smith Household')
);
DELETE FROM org_emails WHERE organization_id IN (
  SELECT id FROM organizations WHERE name IN ('Dallas Dental Group', 'Smith Household')
);
DELETE FROM org_addresses WHERE organization_id IN (
  SELECT id FROM organizations WHERE name IN ('Dallas Dental Group', 'Smith Household')
);
DELETE FROM organizations WHERE name IN ('Dallas Dental Group', 'Smith Household');

-- Clean up business_settings test row
DELETE FROM business_settings WHERE business_name = 'Stitch & Style Embroidery';
" 2>/dev/null

echo "Cleanup complete."

# Verify
remaining=$($MYSQL_CMD "$DB_NAME" -N -e "
SELECT COUNT(*) FROM contacts WHERE $TEST_CONTACTS_WHERE;
" 2>/dev/null)
echo "Remaining test contacts: $remaining"
