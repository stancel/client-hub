#!/usr/bin/env bash
# backup.sh — Database backup for Client Hub
# Designed to be called by cron (daily). Dumps the database, compresses,
# and rotates old backups.
#
# Usage: ./scripts/backup.sh
#
# Environment variables (or set in /opt/client-hub/.env):
#   DB_NAME          Database name (default: clienthub)
#   DB_USER          Database user (default: clienthub)
#   DB_PASSWORD      Database password
#   BACKUP_DIR       Backup directory (default: /opt/client-hub/backups)
#   BACKUP_RETENTION Days to keep backups (default: 7)
#   COMPOSE_FILE     Docker compose file (default: docker-compose.bundled.yml)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if present
if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$PROJECT_DIR/.env"
    set +a
fi

DB_NAME="${DB_NAME:-clienthub}"
DB_USER="${DB_USER:-clienthub}"
DB_PASSWORD="${DB_PASSWORD:-}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
BACKUP_RETENTION="${BACKUP_RETENTION:-7}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.bundled.yml}"
LOG_FILE="${LOG_FILE:-/var/log/client-hub/backup.log}"
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/clienthub-${TIMESTAMP}.sql.gz"

log() {
    local msg="[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1"
    echo "$msg"
    if [[ -d "$(dirname "$LOG_FILE")" ]]; then
        echo "$msg" >> "$LOG_FILE"
    fi
}

mkdir -p "$BACKUP_DIR"

log "Starting backup of ${DB_NAME} to ${BACKUP_FILE}"

# Dump and compress
if docker compose -f "$PROJECT_DIR/$COMPOSE_FILE" exec -T mariadb \
    mariadb-dump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
    2>/dev/null | gzip > "$BACKUP_FILE"; then
    chmod 0600 "$BACKUP_FILE"
    size=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup complete: ${BACKUP_FILE} (${size})"
else
    log "ERROR: Backup failed"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Rotate old backups
deleted=0
if [[ "$BACKUP_RETENTION" -gt 0 ]]; then
    while IFS= read -r old_backup; do
        rm -f "$old_backup"
        deleted=$((deleted + 1))
    done < <(find "$BACKUP_DIR" -name "clienthub-*.sql.gz" -mtime +"$BACKUP_RETENTION" -type f 2>/dev/null)
fi

if [[ "$deleted" -gt 0 ]]; then
    log "Rotated $deleted backup(s) older than $BACKUP_RETENTION days"
fi

log "Backup complete"
