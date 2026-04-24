#!/usr/bin/env bash
# upgrade.sh — Upgrade a deployed Client Hub instance to the latest origin/master
#
# Runs the canonical upgrade sequence from docs/Migration-Strategy.rst:
#   1. Pre-upgrade backup
#   2. git fetch + fast-forward to origin/master
#   3. Stop API + Caddy (mariadb keeps running so migrations can connect)
#   4. Run pending migrations via bootstrap-migrations.sh (idempotent)
#   5. Rebuild the API image
#   6. Start API + Caddy
#   7. Smoke-test the local endpoint
#
# Safe to re-run — each step is idempotent. Prints clear phase headers so
# a human can watch the first upgrade and understand the flow.
#
# Usage:
#   sudo ./scripts/upgrade.sh                   # interactive, pauses between phases
#   sudo ./scripts/upgrade.sh --yes             # non-interactive (future runs / CI)
#   sudo ./scripts/upgrade.sh --skip-backup     # only if a recent backup already exists
#
# Environment / .env variables used:
#   DB_PASSWORD / MARIADB_ROOT_PASSWORD — database passwords
#   API_KEY / CLIENTHUB_ROOT_API_KEY    — for the authenticated smoke test
#   COMPOSE_FILE                         — override; default docker-compose.bundled.yml
#
# Rollback (if this script aborts mid-upgrade):
#   1. gunzip -c backups/<most-recent>.sql.gz | docker exec -i clienthub-mariadb \
#          mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub
#   2. git reset --hard <PRIOR_HEAD> (captured at step 0)
#   3. docker compose -f "$COMPOSE_FILE" up -d --build

set -euo pipefail

# ================================================================
# Defaults + args
# ================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.bundled.yml}"
INTERACTIVE=true
SKIP_BACKUP=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --yes|-y)      INTERACTIVE=false; shift ;;
        --skip-backup) SKIP_BACKUP=true; shift ;;
        --compose)     COMPOSE_FILE="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

cd "$PROJECT_DIR"

# ================================================================
# Colors (only if stdout is a TTY)
# ================================================================
if [[ -t 1 ]]; then
    C_BLUE='\033[1;34m'
    C_GREEN='\033[1;32m'
    C_YELLOW='\033[1;33m'
    C_RED='\033[1;31m'
    C_DIM='\033[2m'
    C_OFF='\033[0m'
else
    C_BLUE='' C_GREEN='' C_YELLOW='' C_RED='' C_DIM='' C_OFF=''
fi

phase()  { printf "\n${C_BLUE}══════════════════════════════════════════════════════════════════\n%s\n══════════════════════════════════════════════════════════════════${C_OFF}\n" "$*"; }
step()   { printf "${C_DIM}→${C_OFF} %s\n" "$*"; }
good()   { printf "${C_GREEN}✓${C_OFF} %s\n" "$*"; }
warn()   { printf "${C_YELLOW}!${C_OFF} %s\n" "$*"; }
fail()   { printf "${C_RED}✗ %s${C_OFF}\n" "$*" >&2; exit 1; }

pause() {
    if $INTERACTIVE; then
        printf "\n${C_YELLOW}⏸  %s ${C_OFF}" "$1"
        read -r _ < /dev/tty || true
    fi
}

# ================================================================
# Pre-flight
# ================================================================
phase "Phase 0 — Pre-flight checks"

[[ -f "$PROJECT_DIR/$COMPOSE_FILE" ]] || fail "Compose file not found: $COMPOSE_FILE"
[[ -f "$PROJECT_DIR/.env" ]]          || fail ".env not found — are you in /opt/client-hub?"

# Load .env (for $MARIADB_ROOT_PASSWORD, $CLIENTHUB_ROOT_API_KEY, etc.)
set -a
# shellcheck disable=SC1091
source "$PROJECT_DIR/.env"
set +a

: "${MARIADB_ROOT_PASSWORD:?MARIADB_ROOT_PASSWORD must be set in .env}"

PRIOR_HEAD=$(git rev-parse HEAD)
step "Current HEAD:          ${PRIOR_HEAD:0:12} ($(git log -1 --format='%s'))"
step "Remote origin:         $(git remote get-url origin)"
step "Compose file:          $COMPOSE_FILE"
step "Interactive mode:      $INTERACTIVE"
step "Skip pre-upgrade backup: $SKIP_BACKUP"

git fetch origin master 2>&1 | sed 's/^/    /'
LATEST=$(git rev-parse origin/master)
step "origin/master HEAD:    ${LATEST:0:12}"

if [[ "$PRIOR_HEAD" == "$LATEST" ]]; then
    good "Already at origin/master — nothing to upgrade."
    exit 0
fi

echo ""
step "Commits about to apply:"
git log --oneline HEAD..origin/master | sed 's/^/    /'

pause "Press ENTER to continue (or Ctrl-C to abort)…"

# ================================================================
# Phase 1 — Backup
# ================================================================
phase "Phase 1 — Pre-upgrade database backup"

if $SKIP_BACKUP; then
    warn "Skipping backup (--skip-backup). Rollback will rely on an existing backup."
else
    ./scripts/backup.sh
    LATEST_BACKUP=$(ls -t backups/clienthub-*.sql.gz 2>/dev/null | head -1 || true)
    [[ -n "$LATEST_BACKUP" ]] || fail "backup.sh did not produce a .sql.gz file"
    good "Backup: $LATEST_BACKUP ($(du -h "$LATEST_BACKUP" | cut -f1))"
fi

pause "Press ENTER after verifying the backup looks reasonable…"

# ================================================================
# Phase 2 — Fast-forward to origin/master
# ================================================================
phase "Phase 2 — git pull origin/master"

git reset --hard origin/master
NEW_HEAD=$(git rev-parse HEAD)
good "HEAD is now ${NEW_HEAD:0:12} ($(git log -1 --format='%s'))"

pause "Press ENTER to stop API + Caddy and run migrations…"

# ================================================================
# Phase 3 — Stop API + Caddy (leave MariaDB running)
# ================================================================
phase "Phase 3 — Stop API + Caddy (MariaDB stays up)"

docker compose -f "$COMPOSE_FILE" stop client-hub-api caddy 2>&1 | sed 's/^/    /' || true

MDB_CONTAINER=$(docker compose -f "$COMPOSE_FILE" ps -q mariadb || true)
[[ -n "$MDB_CONTAINER" ]] || fail "MariaDB container is not running — abort"

docker exec "$MDB_CONTAINER" mariadb-admin ping \
    -u root -p"$MARIADB_ROOT_PASSWORD" --silent 2>/dev/null \
    && good "MariaDB is responding" \
    || fail "MariaDB ping failed"

# ================================================================
# Phase 4 — Run migrations
# ================================================================
phase "Phase 4 — bootstrap-migrations.sh"

step "Migrations tracked in _schema_migrations — only new ones apply."

# bootstrap-migrations.sh talks to mariadb on 127.0.0.1:3306 — that works
# because the compose file publishes 3306. If your bundled compose has
# mariadb bound to a custom port, override DB_HOST/DB_PORT in .env.
DB_HOST="${DB_HOST:-127.0.0.1}" \
DB_PORT="${DB_PORT:-3306}" \
DB_NAME="${DB_NAME:-clienthub}" \
DB_USER="root" \
DB_PASSWORD="$MARIADB_ROOT_PASSWORD" \
./scripts/bootstrap-migrations.sh 2>&1 | sed 's/^/    /'

# Quick post-migration sanity check
docker exec "$MDB_CONTAINER" mariadb -u root -p"$MARIADB_ROOT_PASSWORD" \
    "${DB_NAME:-clienthub}" -e "
SELECT version FROM _schema_migrations
 WHERE version LIKE '019_%' OR version LIKE '020_%'
    OR version LIKE '021_%' OR version LIKE '022_%'
 ORDER BY version;" 2>/dev/null | sed 's/^/    /'

pause "Press ENTER to rebuild the API image and bring everything back up…"

# ================================================================
# Phase 5 — Rebuild + start
# ================================================================
phase "Phase 5 — Rebuild API image and start services"

docker compose -f "$COMPOSE_FILE" build client-hub-api 2>&1 | tail -15 | sed 's/^/    /'
docker compose -f "$COMPOSE_FILE" up -d 2>&1 | sed 's/^/    /'
sleep 5

docker compose -f "$COMPOSE_FILE" ps 2>&1 | sed 's/^/    /'

# ================================================================
# Phase 6 — Smoke test
# ================================================================
phase "Phase 6 — Smoke test"

SMOKE_ARGS=("--url" "http://127.0.0.1:8800")
if [[ -n "${CLIENTHUB_ROOT_API_KEY:-}" ]]; then
    SMOKE_ARGS+=("--api-key" "$CLIENTHUB_ROOT_API_KEY")
elif [[ -n "${API_KEY:-}" ]]; then
    SMOKE_ARGS+=("--api-key" "$API_KEY")
fi

./scripts/smoke-test.sh "${SMOKE_ARGS[@]}" 2>&1 | sed 's/^/    /'

# Extra targeted check: the new /affiliations route must be registered.
AFF_COUNT=$(curl -sf http://127.0.0.1:8800/openapi.json 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); \
        print(sum(1 for p in d['paths'] if 'affiliations' in p))" 2>/dev/null || echo 0)
if [[ "$AFF_COUNT" -ge 2 ]]; then
    good "/affiliations endpoints registered in OpenAPI ($AFF_COUNT paths)"
else
    fail "/affiliations endpoints NOT found in OpenAPI — new code may not be live"
fi

# ================================================================
# Done
# ================================================================
phase "Upgrade complete"

good "Previous HEAD: ${PRIOR_HEAD:0:12}"
good "Current HEAD:  ${NEW_HEAD:0:12}"
echo ""
step "Monitor logs for a few minutes:"
step "    docker compose -f $COMPOSE_FILE logs --tail=100 -f client-hub-api"
echo ""
step "If anything goes wrong, rollback:"
step "    gunzip -c $LATEST_BACKUP | docker exec -i \$(docker compose -f $COMPOSE_FILE ps -q mariadb) \\"
step "        mariadb -u root -p\$MARIADB_ROOT_PASSWORD ${DB_NAME:-clienthub}"
step "    git reset --hard $PRIOR_HEAD"
step "    docker compose -f $COMPOSE_FILE up -d --build"
