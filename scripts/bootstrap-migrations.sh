#!/usr/bin/env bash
# bootstrap-migrations.sh — Idempotent migration runner for Client Hub
# Uses the _schema_migrations table to track which migrations have been applied.
# Safe to run multiple times.
#
# Usage: ./scripts/bootstrap-migrations.sh [options]
#   --host HOST          MariaDB host (default: 127.0.0.1)
#   --port PORT          MariaDB port (default: 3306)
#   --user USER          MariaDB user (default: root)
#   --password PASS      MariaDB password
#   --database DB        Database name (default: clienthub)
#   --migrations DIR     Migrations directory (default: ./migrations)
#   --with-seed-data     Also run migrations from migrations/dev/ (test data)

set -euo pipefail

# Defaults
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-clienthub}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-./migrations}"
WITH_SEED_DATA=false

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)            DB_HOST="$2"; shift 2 ;;
        --port)            DB_PORT="$2"; shift 2 ;;
        --user)            DB_USER="$2"; shift 2 ;;
        --password)        DB_PASSWORD="$2"; shift 2 ;;
        --database)        DB_NAME="$2"; shift 2 ;;
        --migrations)      MIGRATIONS_DIR="$2"; shift 2 ;;
        --with-seed-data)  WITH_SEED_DATA=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

MYSQL_CMD="mariadb -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USER}"
if [[ -n "$DB_PASSWORD" ]]; then
    MYSQL_CMD="$MYSQL_CMD -p${DB_PASSWORD}"
fi

echo "=== Client Hub Migration Runner ==="
echo "Database: ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
if $WITH_SEED_DATA; then
    echo "Seed data: INCLUDED (--with-seed-data)"
else
    echo "Seed data: SKIPPED (use --with-seed-data to include)"
fi
echo ""

# Step 1: Ensure _schema_migrations table exists
$MYSQL_CMD "$DB_NAME" -e "
CREATE TABLE IF NOT EXISTS _schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
" 2>/dev/null

# Step 2: Apply migrations from a directory
apply_migrations() {
    local dir="$1"
    local prefix="$2"
    local applied=0
    local skipped=0

    for migration_file in "$dir"/*.sql; do
        if [[ ! -f "$migration_file" ]]; then
            return
        fi

        version="${prefix}$(basename "$migration_file")"

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

    echo "  Applied: $applied, Skipped: $skipped"
}

echo "--- Schema migrations ---"
apply_migrations "$MIGRATIONS_DIR" ""

# Step 3: Apply dev/seed migrations if requested
if $WITH_SEED_DATA && [[ -d "$MIGRATIONS_DIR/dev" ]]; then
    echo ""
    echo "--- Dev/seed data migrations ---"
    apply_migrations "$MIGRATIONS_DIR/dev" "dev/"
fi

echo ""
echo "Migration run complete."
