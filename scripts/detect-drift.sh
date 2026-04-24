#!/usr/bin/env bash
# detect-drift.sh — Check a Client Hub DB for schema drift from the canonical
# types declared in migrations/*.sql.
#
# Originally written after the 2026-04-24 Clever Orchid upgrade, where the
# existing install had every integer column as `int(11)` (signed 32-bit)
# instead of the canonical `BIGINT UNSIGNED`. FK types in migration 019
# couldn't be created because they can only reference columns of matching
# type. Root cause never identified, but both deployed VPSes were checked
# with this script to know which upgrade path (normal vs rebuild) to use.
#
# Run this BEFORE any upgrade that adds FK columns. Exit codes:
#   0  — no drift detected (safe to run normal upgrade)
#   1  — drift detected (schema rebuild from canonical migrations required)
#   2  — usage error / cannot connect
#
# Usage:
#   ./scripts/detect-drift.sh                         # host client on 127.0.0.1:3306
#   ./scripts/detect-drift.sh --via-docker clienthub-mariadb
#
# Loads DB credentials from ./.env if present (MARIADB_ROOT_PASSWORD,
# DB_NAME), same pattern as backup.sh.

set -euo pipefail

# Prefer the current working directory's .env — this script is meant to be
# run from the install dir (e.g. /opt/client-hub). Fall back to the script's
# parent dir for convenience when run in place inside a checkout.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "./.env" ]]; then
    PROJECT_DIR="$(pwd)"
else
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
fi

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-clienthub}"
VIA_DOCKER="${VIA_DOCKER:-}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)         DB_HOST="$2"; shift 2 ;;
        --port)         DB_PORT="$2"; shift 2 ;;
        --user)         DB_USER="$2"; shift 2 ;;
        --password)     DB_PASSWORD="$2"; shift 2 ;;
        --database)     DB_NAME="$2"; shift 2 ;;
        --via-docker)   VIA_DOCKER="$2"; shift 2 ;;
        -h|--help)      sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)              echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

# Load .env for MARIADB_ROOT_PASSWORD etc. (same convention as backup.sh)
if [[ -f "$PROJECT_DIR/.env" && -z "$DB_PASSWORD" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$PROJECT_DIR/.env"
    set +a
    DB_PASSWORD="${DB_PASSWORD:-${MARIADB_ROOT_PASSWORD:-}}"
fi

if [[ -n "$VIA_DOCKER" ]]; then
    MYSQL_CMD=(docker exec -i "$VIA_DOCKER" mariadb -u "$DB_USER")
else
    MYSQL_CMD=(mariadb -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER")
fi
[[ -n "$DB_PASSWORD" ]] && MYSQL_CMD+=("-p$DB_PASSWORD")

echo "=== Client Hub schema drift check ==="
if [[ -n "$VIA_DOCKER" ]]; then
    echo "Target: $DB_NAME via docker exec $VIA_DOCKER"
else
    echo "Target: $DB_NAME @ $DB_HOST:$DB_PORT"
fi
echo ""

# Canonical canary: contacts.id should be BIGINT UNSIGNED per migrations/004_contacts.sql.
# If this one's wrong, the whole DB has the same drift (observed 2026-04-24).
# xargs trims leading/trailing whitespace WITHOUT collapsing internal spaces —
# we need that because the canonical type string is `bigint(20) unsigned`
# with a real space inside.
CANARY=$("${MYSQL_CMD[@]}" "$DB_NAME" -N -e "
SELECT COLUMN_TYPE FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = '$DB_NAME' AND TABLE_NAME = 'contacts' AND COLUMN_NAME = 'id';
" 2>/dev/null | xargs)

if [[ -z "$CANARY" ]]; then
    echo "ERROR: could not read contacts.id type — does table exist?" >&2
    exit 2
fi

echo "contacts.id current type:     $CANARY"
echo "contacts.id canonical type:   bigint(20) unsigned"
echo ""

if [[ "$CANARY" == "bigint(20) unsigned" ]]; then
    echo "RESULT: No drift detected. Safe to use the standard upgrade path"
    echo "        (./scripts/upgrade.sh or ./scripts/bootstrap-migrations.sh)."
    exit 0
fi

# Drift detected — give an operator-useful count of affected columns
DRIFTED=$("${MYSQL_CMD[@]}" "$DB_NAME" -N -e "
SELECT COUNT(*) FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = '$DB_NAME' AND COLUMN_TYPE LIKE 'int(%';
" 2>/dev/null | tr -d '[:space:]')

cat <<EOF
RESULT: DRIFT DETECTED.

  $DRIFTED integer columns DB-wide are NOT the canonical BIGINT UNSIGNED.
  The standard upgrade path will fail at the first migration that adds a
  new FK referencing contacts(id) or organizations(id).

  Recommended path: rebuild the schema from canonical migrations, preserving
  data via a data-only dump. See the 2026-04-24 CHANGELOG entry for the
  exact sequence used on the Clever Orchid VPS.

EOF
exit 1
