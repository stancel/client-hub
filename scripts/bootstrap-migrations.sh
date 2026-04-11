#!/usr/bin/env bash
# bootstrap-migrations.sh — Idempotent migration runner for Client Hub
# Uses the _schema_migrations table to track which migrations have been applied.
# Safe to run multiple times.
#
# Usage: ./scripts/bootstrap-migrations.sh [options]
#   --host HOST      MariaDB host (default: 127.0.0.1)
#   --port PORT      MariaDB port (default: 3306)
#   --user USER      MariaDB user (default: root)
#   --password PASS  MariaDB password
#   --database DB    Database name (default: clienthub)
#   --migrations DIR Migrations directory (default: ./migrations)

set -euo pipefail

# Defaults
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-clienthub}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-./migrations}"

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)      DB_HOST="$2"; shift 2 ;;
        --port)      DB_PORT="$2"; shift 2 ;;
        --user)      DB_USER="$2"; shift 2 ;;
        --password)  DB_PASSWORD="$2"; shift 2 ;;
        --database)  DB_NAME="$2"; shift 2 ;;
        --migrations) MIGRATIONS_DIR="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

MYSQL_CMD="mariadb -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USER}"
if [[ -n "$DB_PASSWORD" ]]; then
    MYSQL_CMD="$MYSQL_CMD -p${DB_PASSWORD}"
fi

echo "=== Client Hub Migration Runner ==="
echo "Database: ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
echo ""

# Step 1: Ensure _schema_migrations table exists
$MYSQL_CMD "$DB_NAME" -e "
CREATE TABLE IF NOT EXISTS _schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
" 2>/dev/null

# Step 2: Apply each migration in order if not already applied
applied=0
skipped=0

for migration_file in "$MIGRATIONS_DIR"/*.sql; do
    if [[ ! -f "$migration_file" ]]; then
        echo "No migration files found in $MIGRATIONS_DIR"
        exit 0
    fi

    version=$(basename "$migration_file")

    # Check if already applied
    already_applied=$($MYSQL_CMD "$DB_NAME" -N -e \
        "SELECT COUNT(*) FROM _schema_migrations WHERE version = '${version}';" 2>/dev/null)

    if [[ "$already_applied" -gt 0 ]]; then
        skipped=$((skipped + 1))
        continue
    fi

    echo "Applying: $version ..."
    if $MYSQL_CMD "$DB_NAME" < "$migration_file" 2>&1; then
        $MYSQL_CMD "$DB_NAME" -e \
            "INSERT INTO _schema_migrations (version) VALUES ('${version}');" 2>/dev/null
        applied=$((applied + 1))
        echo "  OK"
    else
        echo "  FAILED — aborting"
        exit 1
    fi
done

echo ""
echo "Done. Applied: $applied, Skipped (already applied): $skipped"
