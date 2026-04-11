#!/usr/bin/env bash
# install.sh — One-line installer for Client Hub
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh | sudo bash
#
# Non-interactive:
#   curl -fsSL ... | sudo bash -s -- \
#     --mode bundled \
#     --domain client-hub.example.com \
#     --admin-email admin@example.com \
#     --first-source-code my_website \
#     --first-source-name "My Website" \
#     --sdks typescript \
#     --non-interactive

set -euo pipefail

# ============================================================
# Defaults
# ============================================================
INSTALL_DIR="/opt/client-hub"
REPO_URL="https://github.com/stancel/client-hub"
MODE="bundled"
DOMAIN=""
ADMIN_EMAIL=""
FIRST_SOURCE_CODE="bootstrap"
FIRST_SOURCE_NAME="Bootstrap Source"
SDK_LANG="none"
NON_INTERACTIVE=false
MIN_RAM_MB=1024
MIN_DISK_GB=10

# ============================================================
# Parse arguments
# ============================================================
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)               MODE="$2"; shift 2 ;;
        --domain)             DOMAIN="$2"; shift 2 ;;
        --admin-email)        ADMIN_EMAIL="$2"; shift 2 ;;
        --first-source-code)  FIRST_SOURCE_CODE="$2"; shift 2 ;;
        --first-source-name)  FIRST_SOURCE_NAME="$2"; shift 2 ;;
        --sdks)               SDK_LANG="$2"; shift 2 ;;
        --non-interactive)    NON_INTERACTIVE=true; shift ;;
        --install-dir)        INSTALL_DIR="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ============================================================
# Helpers
# ============================================================
log()  { echo "[client-hub] $*"; }
warn() { echo "[client-hub] WARNING: $*" >&2; }
fail() { echo "[client-hub] FATAL: $*" >&2; exit 1; }

prompt() {
    local var_name="$1" prompt_text="$2" default="$3"
    if $NON_INTERACTIVE; then
        eval "$var_name=\"$default\""
        return
    fi
    read -rp "$prompt_text [$default]: " input
    eval "$var_name=\"${input:-$default}\""
}

# ============================================================
# Pre-flight checks
# ============================================================
log "=== Client Hub Installer ==="
echo ""

# Must be root
if [[ "$(id -u)" -ne 0 ]]; then
    fail "Must run as root. Use: curl ... | sudo bash"
fi

# OS detection
if [[ ! -f /etc/os-release ]]; then
    fail "Cannot detect OS. /etc/os-release not found."
fi
# shellcheck source=/dev/null
source /etc/os-release
case "$ID" in
    ubuntu|debian) log "Detected OS: $PRETTY_NAME" ;;
    *) fail "Unsupported OS: $ID. Only Ubuntu (22.04/24.04) and Debian (12+) are supported." ;;
esac

# Hardware check
avail_ram_mb=$(awk '/MemAvailable/ {printf "%.0f", $2/1024}' /proc/meminfo)
avail_disk_gb=$(df -BG "$INSTALL_DIR" 2>/dev/null | awk 'NR==2 {print $4}' | tr -d 'G' || df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')

if [[ "$avail_ram_mb" -lt 512 ]]; then
    fail "Only ${avail_ram_mb}MB RAM available. Minimum 512MB required. Resize your VPS."
fi
if [[ "$avail_ram_mb" -lt "$MIN_RAM_MB" ]]; then
    warn "Only ${avail_ram_mb}MB RAM available (recommended: ${MIN_RAM_MB}MB). Proceeding anyway."
fi
if [[ "$avail_disk_gb" -lt 5 ]]; then
    fail "Only ${avail_disk_gb}GB disk available. Minimum 5GB required."
fi
if [[ "$avail_disk_gb" -lt "$MIN_DISK_GB" ]]; then
    warn "Only ${avail_disk_gb}GB disk available (recommended: ${MIN_DISK_GB}GB)."
fi

log "RAM: ${avail_ram_mb}MB available, Disk: ${avail_disk_gb}GB available"

# ============================================================
# Interactive prompts
# ============================================================
if ! $NON_INTERACTIVE; then
    echo ""
    prompt DOMAIN "Domain name (leave blank for no TLS)" "$DOMAIN"
    if [[ -n "$DOMAIN" ]]; then
        prompt ADMIN_EMAIL "Admin email (for Let's Encrypt)" "$ADMIN_EMAIL"
    fi
    prompt FIRST_SOURCE_CODE "First source code (slug)" "$FIRST_SOURCE_CODE"
    prompt FIRST_SOURCE_NAME "First source display name" "$FIRST_SOURCE_NAME"
    prompt SDK_LANG "SDK languages to generate (all/python/php/typescript/none)" "$SDK_LANG"
    echo ""
fi

# ============================================================
# Install prerequisites
# ============================================================
log "Installing prerequisites..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq ca-certificates curl openssl gnupg ufw mariadb-client cron git >/dev/null 2>&1

# Docker
if ! command -v docker &>/dev/null; then
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | sh >/dev/null 2>&1
fi

# Docker Compose plugin
if ! docker compose version &>/dev/null; then
    log "Installing docker-compose plugin..."
    apt-get install -y -qq docker-compose-plugin >/dev/null 2>&1
fi

docker compose version >/dev/null 2>&1 || fail "docker compose not working"
log "Docker ready: $(docker --version | head -1)"

# ============================================================
# System user + directories
# ============================================================
if ! id clienthub &>/dev/null; then
    log "Creating clienthub system user..."
    useradd --system --no-create-home --shell /usr/sbin/nologin clienthub
    usermod -aG docker clienthub
fi

mkdir -p "$INSTALL_DIR" "$INSTALL_DIR/backups" /var/log/client-hub
chown clienthub:clienthub "$INSTALL_DIR" "$INSTALL_DIR/backups" /var/log/client-hub
chmod 0750 "$INSTALL_DIR"
chmod 0700 "$INSTALL_DIR/backups"
chmod 0750 /var/log/client-hub

# ============================================================
# Download source
# ============================================================
if [[ -n "${CLIENTHUB_TARBALL_URL:-}" ]]; then
    log "Downloading from tarball: $CLIENTHUB_TARBALL_URL"
    curl -fsSL "$CLIENTHUB_TARBALL_URL" | tar -xz -C "$INSTALL_DIR" --strip-components=1
else
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        log "Updating existing repo..."
        cd "$INSTALL_DIR" && git pull --ff-only
    else
        log "Cloning repository..."
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
fi

cd "$INSTALL_DIR"

# ============================================================
# Generate secrets
# ============================================================
log "Generating secrets..."
MARIADB_ROOT_PASSWORD=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 32)
CLIENTHUB_ROOT_API_KEY=$(openssl rand -hex 32)
FIRST_SOURCE_API_KEY=$(openssl rand -hex 32)

# ============================================================
# Write .env
# ============================================================
log "Writing configuration..."
cat > "$INSTALL_DIR/.env" <<ENVEOF
# Client Hub — Generated by install.sh on $(date -u +%Y-%m-%dT%H:%M:%SZ)
MODE=$MODE
DOMAIN=$DOMAIN
ADMIN_EMAIL=$ADMIN_EMAIL
DB_NAME=clienthub
DB_USER=clienthub
DB_PASSWORD=$DB_PASSWORD
MARIADB_ROOT_PASSWORD=$MARIADB_ROOT_PASSWORD
CLIENTHUB_ROOT_API_KEY=$CLIENTHUB_ROOT_API_KEY
API_KEY=$CLIENTHUB_ROOT_API_KEY
TZ=UTC
ENVEOF

chown clienthub:clienthub "$INSTALL_DIR/.env"
chmod 0600 "$INSTALL_DIR/.env"

# ============================================================
# Choose compose file and start
# ============================================================
if [[ -n "$DOMAIN" ]]; then
    COMPOSE_FILE="docker-compose.bundled.yml"
    log "Mode: bundled with TLS (domain: $DOMAIN)"
else
    COMPOSE_FILE="docker-compose.bundled-nodomain.yml"
    warn "No domain provided. API will be exposed on port 8800 without TLS."
fi

log "Pulling images..."
docker compose -f "$COMPOSE_FILE" pull 2>/dev/null || true

log "Building API image..."
docker compose -f "$COMPOSE_FILE" build --quiet 2>/dev/null

log "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d

# Wait for MariaDB
log "Waiting for MariaDB..."
for i in $(seq 1 60); do
    if docker compose -f "$COMPOSE_FILE" exec -T mariadb \
        mariadb-admin ping -u root -p"$MARIADB_ROOT_PASSWORD" &>/dev/null; then
        break
    fi
    sleep 2
done

# Verify MariaDB is up
docker compose -f "$COMPOSE_FILE" exec -T mariadb \
    mariadb-admin ping -u root -p"$MARIADB_ROOT_PASSWORD" &>/dev/null \
    || fail "MariaDB did not start within 120 seconds"

log "MariaDB is ready"

# ============================================================
# Run migrations
# ============================================================
log "Running migrations..."

# Use mariadb client inside the container
run_sql() {
    docker compose -f "$COMPOSE_FILE" exec -T mariadb \
        mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub -e "$1" 2>/dev/null
}

# Create tracking table first
run_sql "CREATE TABLE IF NOT EXISTS _schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"

# Apply each migration idempotently
for migration_file in migrations/*.sql; do
    version=$(basename "$migration_file")
    already=$(run_sql "SELECT COUNT(*) FROM _schema_migrations WHERE version = '${version}';" | tail -1 | tr -d '[:space:]')
    if [[ "$already" -gt 0 ]]; then
        continue
    fi
    log "  Applying: $version"
    docker compose -f "$COMPOSE_FILE" exec -T mariadb \
        mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub < "$migration_file" 2>/dev/null \
        || fail "Migration failed: $version"
    run_sql "INSERT INTO _schema_migrations (version) VALUES ('${version}');"
done

log "Migrations complete"

# ============================================================
# Setup first source + API key
# ============================================================
log "Configuring first source..."

# Wait for API to be ready
for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:8800/api/v1/health &>/dev/null; then
        break
    fi
    sleep 2
done

curl -sf http://127.0.0.1:8800/api/v1/health &>/dev/null \
    || fail "API did not become healthy within 60 seconds"

# Create source if not bootstrap
if [[ "$FIRST_SOURCE_CODE" != "bootstrap" ]]; then
    curl -sf -X POST \
        -H "X-API-Key: $CLIENTHUB_ROOT_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"code\": \"$FIRST_SOURCE_CODE\", \"name\": \"$FIRST_SOURCE_NAME\", \"source_type\": \"website\"}" \
        http://127.0.0.1:8800/api/v1/admin/sources >/dev/null
    FIRST_SOURCE_UUID=$(curl -sf -H "X-API-Key: $CLIENTHUB_ROOT_API_KEY" \
        http://127.0.0.1:8800/api/v1/admin/sources \
        | python3 -c "import sys,json; sources=json.load(sys.stdin)['data']; print(next(s['uuid'] for s in sources if s['code']=='$FIRST_SOURCE_CODE'))")
else
    FIRST_SOURCE_UUID=$(curl -sf -H "X-API-Key: $CLIENTHUB_ROOT_API_KEY" \
        http://127.0.0.1:8800/api/v1/admin/sources \
        | python3 -c "import sys,json; sources=json.load(sys.stdin)['data']; print(next(s['uuid'] for s in sources if s['code']=='bootstrap'))")
fi

# Insert API key directly into DB (we have the pre-generated key)
KEY_PREFIX="${FIRST_SOURCE_API_KEY:0:8}"
run_sql "INSERT INTO api_keys (uuid, source_id, key_prefix, key_value, name)
SELECT UUID(), s.id, '${KEY_PREFIX}', '${FIRST_SOURCE_API_KEY}', 'Install-generated key'
FROM sources s WHERE s.code = '${FIRST_SOURCE_CODE}';"

# ============================================================
# Firewall
# ============================================================
log "Configuring firewall..."
ufw default deny incoming >/dev/null 2>&1
ufw default allow outgoing >/dev/null 2>&1
ufw allow 22/tcp >/dev/null 2>&1
if [[ -n "$DOMAIN" ]]; then
    ufw allow 80/tcp >/dev/null 2>&1
    ufw allow 443/tcp >/dev/null 2>&1
else
    ufw allow 8800/tcp >/dev/null 2>&1
    warn "Port 8800 exposed without TLS. Consider adding a domain."
fi
ufw --force enable >/dev/null 2>&1

# ============================================================
# Backup cron
# ============================================================
log "Setting up nightly backup..."
chmod +x "$INSTALL_DIR/scripts/backup.sh"
cat > /etc/cron.daily/client-hub-backup <<CRONEOF
#!/bin/bash
COMPOSE_FILE=$COMPOSE_FILE $INSTALL_DIR/scripts/backup.sh
CRONEOF
chmod +x /etc/cron.daily/client-hub-backup

# ============================================================
# SDK generation (optional)
# ============================================================
if [[ "$SDK_LANG" != "none" ]]; then
    log "Generating SDKs ($SDK_LANG)..."
    chmod +x "$INSTALL_DIR/scripts/generate-sdks.sh"
    CLIENT_HUB_API_URL="http://127.0.0.1:8800" "$INSTALL_DIR/scripts/generate-sdks.sh" "$SDK_LANG" || warn "SDK generation failed (non-fatal)"
fi

# ============================================================
# Smoke test
# ============================================================
log "Running smoke test..."
chmod +x "$INSTALL_DIR/scripts/smoke-test.sh"
"$INSTALL_DIR/scripts/smoke-test.sh" --url http://127.0.0.1:8800 --api-key "$CLIENTHUB_ROOT_API_KEY" || warn "Some smoke tests failed"

# ============================================================
# Determine API URL for display
# ============================================================
if [[ -n "$DOMAIN" ]]; then
    API_URL_DISPLAY="https://$DOMAIN"
else
    API_URL_DISPLAY="http://$(hostname -I | awk '{print $1}'):8800"
fi

# ============================================================
# Install summary
# ============================================================
SUMMARY="=====================================================
Client Hub Installation Complete
=====================================================

Install path:  $INSTALL_DIR
Mode:          $MODE
Domain:        ${DOMAIN:-none (plain HTTP on port 8800)}
API URL:       $API_URL_DISPLAY
Swagger UI:    $API_URL_DISPLAY/docs

Credentials (SAVE THESE — also in $INSTALL_DIR/.install-summary):

  Root API key (admin, cross-source):
    $CLIENTHUB_ROOT_API_KEY

  First source code:
    $FIRST_SOURCE_CODE

  First source API key (write, source-scoped):
    $FIRST_SOURCE_API_KEY

  MariaDB root password:
    $MARIADB_ROOT_PASSWORD

  MariaDB clienthub password:
    $DB_PASSWORD

Next steps:

  1. Save these credentials in a password manager immediately.
  2. Test the API (admin):
     curl -H \"X-API-Key: $CLIENTHUB_ROOT_API_KEY\" $API_URL_DISPLAY/api/v1/health
  3. Test the API (source):
     curl -H \"X-API-Key: $FIRST_SOURCE_API_KEY\" $API_URL_DISPLAY/api/v1/contacts
  4. Create additional sources via the admin API as needed.
  5. Start pushing events from your sites/integrations.

Logs:
  docker compose -f $INSTALL_DIR/$COMPOSE_FILE logs -f

Backups: $INSTALL_DIR/backups/ (nightly, 7-day retention)

Uninstall: sudo $INSTALL_DIR/scripts/uninstall.sh
====================================================="

echo "$SUMMARY" | tee "$INSTALL_DIR/.install-summary"
chown clienthub:clienthub "$INSTALL_DIR/.install-summary"
chmod 0600 "$INSTALL_DIR/.install-summary"

log "Installation complete!"
