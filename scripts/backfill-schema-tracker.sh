#!/usr/bin/env bash
# backfill-schema-tracker.sh — Record pre-existing migrations in _schema_migrations.
#
# The _schema_migrations tracker table was introduced in migration 018.
# Any Client Hub install created before that migration lands has an empty
# tracker, which makes bootstrap-migrations.sh think nothing's been applied
# and re-attempt every migration — tripping on non-idempotent ALTERs in
# early migrations (e.g. 013's ADD COLUMN without IF NOT EXISTS).
#
# Run this ONCE on old installs to record the actual applied state, then
# future runs of bootstrap-migrations.sh will correctly skip them and only
# apply new migrations.
#
# Usage:
#   sudo ./scripts/backfill-schema-tracker.sh \
#        --through 018_schema_migrations_tracking.sql \
#        --via-docker clienthub-mariadb
#
# Flags:
#   --through VERSION         Record every migration file up to and including
#                             this filename (e.g. 018_schema_migrations_tracking.sql).
#                             REQUIRED. Use the exact basename from migrations/.
#   --database DB             Database name (default: clienthub).
#   --migrations DIR          Migrations directory (default: ./migrations).
#   --via-docker CONTAINER    Run mariadb commands via docker exec. Omit to
#                             use the host mariadb client on 127.0.0.1:3306.
#   --host/--port/--user/--password  Same as bootstrap-migrations.sh.
#   --dry-run                 Print what would be inserted; change nothing.
#
# Safe to re-run — INSERT IGNORE makes duplicates no-ops.

set -euo pipefail

# Defaults
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-clienthub}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-./migrations}"
VIA_DOCKER="${VIA_DOCKER:-}"
THROUGH=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --through)      THROUGH="$2"; shift 2 ;;
        --host)         DB_HOST="$2"; shift 2 ;;
        --port)         DB_PORT="$2"; shift 2 ;;
        --user)         DB_USER="$2"; shift 2 ;;
        --password)     DB_PASSWORD="$2"; shift 2 ;;
        --database)     DB_NAME="$2"; shift 2 ;;
        --migrations)   MIGRATIONS_DIR="$2"; shift 2 ;;
        --via-docker)   VIA_DOCKER="$2"; shift 2 ;;
        --dry-run)      DRY_RUN=true; shift ;;
        -h|--help)      sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)              echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

[[ -n "$THROUGH" ]] || { echo "--through VERSION is required" >&2; exit 2; }
[[ -d "$MIGRATIONS_DIR" ]] || { echo "Migrations dir not found: $MIGRATIONS_DIR" >&2; exit 2; }

# Build mariadb command array (same pattern as bootstrap-migrations.sh)
if [[ -n "$VIA_DOCKER" ]]; then
    MYSQL_CMD=(docker exec -i "$VIA_DOCKER" mariadb -u "$DB_USER")
else
    MYSQL_CMD=(mariadb -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER")
fi
[[ -n "$DB_PASSWORD" ]] && MYSQL_CMD+=("-p$DB_PASSWORD")

echo "=== Schema tracker backfill ==="
if [[ -n "$VIA_DOCKER" ]]; then
    echo "Database:   ${DB_NAME} via docker exec ${VIA_DOCKER}"
else
    echo "Database:   ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
fi
echo "Migrations: $MIGRATIONS_DIR"
echo "Through:    $THROUGH"
echo ""

# Ensure tracker table exists (harmless if it already does)
"${MYSQL_CMD[@]}" "$DB_NAME" -e "
CREATE TABLE IF NOT EXISTS _schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;" 2>/dev/null

# Build the list of versions to record — every .sql in lexicographic order
# up to and including THROUGH.
versions=()
reached=false
for f in "$MIGRATIONS_DIR"/*.sql; do
    [[ -f "$f" ]] || continue
    basename=$(basename "$f")
    versions+=("$basename")
    if [[ "$basename" == "$THROUGH" ]]; then
        reached=true
        break
    fi
done

if ! $reached; then
    echo "ERROR: --through $THROUGH did not match any file in $MIGRATIONS_DIR" >&2
    exit 1
fi

echo "Recording ${#versions[@]} versions as applied:"
for v in "${versions[@]}"; do
    echo "  $v"
done

if $DRY_RUN; then
    echo ""
    echo "--dry-run — nothing inserted."
    exit 0
fi

# Emit a single INSERT IGNORE with all values
values=""
for v in "${versions[@]}"; do
    [[ -n "$values" ]] && values+=","
    values+="('$v')"
done

"${MYSQL_CMD[@]}" "$DB_NAME" -e "
INSERT IGNORE INTO _schema_migrations (version) VALUES $values;
SELECT COUNT(*) AS tracked FROM _schema_migrations;" 2>/dev/null

echo ""
echo "Backfill complete. Future ./scripts/bootstrap-migrations.sh runs will skip these."
