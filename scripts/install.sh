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
#     --first-source-code my_business_website \
#     --first-source-name "My Business Website" \
#     --first-source-domain mybusiness.com \
#     --business-name "My Business, LLC" \
#     --business-type embroidery \
#     --business-timezone America/New_York \
#     --business-email contact@mybusiness.com \
#     --sdks typescript \
#     --non-interactive
#
# Source-discipline rule: every install MUST create a properly-named
# consumer-site source on day one. The seeded ``bootstrap`` row is for
# the very first request that sets up the system — it should be
# renamed (one-tenant case) or supplemented with named sources
# (multi-source case) and never used as a runtime identity. See
# docs/Sources.rst.

set -euo pipefail

# ============================================================
# Defaults
# ============================================================
INSTALL_DIR="/opt/client-hub"
REPO_URL="https://github.com/stancel/client-hub"
MODE="bundled"
DOMAIN=""
ADMIN_EMAIL=""
FIRST_SOURCE_CODE=""
FIRST_SOURCE_NAME=""
FIRST_SOURCE_DOMAIN=""
FIRST_SOURCE_TYPE="website"
# Business profile (populates the business_settings singleton).
# business_name is required (NOT NULL); the rest are optional but
# always nice to have for invoice headers, emails, audit logs.
BUSINESS_NAME=""
BUSINESS_TYPE=""
BUSINESS_TIMEZONE="America/New_York"
BUSINESS_CURRENCY="USD"
BUSINESS_COUNTRY="US"
BUSINESS_PHONE=""
BUSINESS_EMAIL=""
BUSINESS_WEBSITE=""
SDK_LANG="none"
INCLUDE_SEED_DATA=false
NON_INTERACTIVE=false
MIN_RAM_MB=1024
MIN_DISK_GB=10

# ============================================================
# Parse arguments
# ============================================================
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)                  MODE="$2"; shift 2 ;;
        --domain)                DOMAIN="$2"; shift 2 ;;
        --admin-email)           ADMIN_EMAIL="$2"; shift 2 ;;
        --first-source-code)     FIRST_SOURCE_CODE="$2"; shift 2 ;;
        --first-source-name)     FIRST_SOURCE_NAME="$2"; shift 2 ;;
        --first-source-domain)   FIRST_SOURCE_DOMAIN="$2"; shift 2 ;;
        --first-source-type)     FIRST_SOURCE_TYPE="$2"; shift 2 ;;
        --business-name)         BUSINESS_NAME="$2"; shift 2 ;;
        --business-type)         BUSINESS_TYPE="$2"; shift 2 ;;
        --business-timezone)     BUSINESS_TIMEZONE="$2"; shift 2 ;;
        --business-currency)     BUSINESS_CURRENCY="$2"; shift 2 ;;
        --business-country)      BUSINESS_COUNTRY="$2"; shift 2 ;;
        --business-phone)        BUSINESS_PHONE="$2"; shift 2 ;;
        --business-email)        BUSINESS_EMAIL="$2"; shift 2 ;;
        --business-website)      BUSINESS_WEBSITE="$2"; shift 2 ;;
        --sdks)                  SDK_LANG="$2"; shift 2 ;;
        --include-seed-data)     INCLUDE_SEED_DATA=true; shift ;;
        --non-interactive)       NON_INTERACTIVE=true; shift ;;
        --install-dir)           INSTALL_DIR="$2"; shift 2 ;;
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
    echo ""
    echo "--- Business profile (populates business_settings) ---"
    prompt BUSINESS_NAME     "Business name (required)"          "$BUSINESS_NAME"
    prompt BUSINESS_TYPE     "Business type (e.g. dental)"       "$BUSINESS_TYPE"
    prompt BUSINESS_TIMEZONE "Timezone (IANA)"                   "$BUSINESS_TIMEZONE"
    prompt BUSINESS_CURRENCY "Currency (ISO 4217)"               "$BUSINESS_CURRENCY"
    prompt BUSINESS_COUNTRY  "Country code (ISO 3166-1 alpha-2)" "$BUSINESS_COUNTRY"
    prompt BUSINESS_PHONE    "Business phone (optional)"         "$BUSINESS_PHONE"
    prompt BUSINESS_EMAIL    "Business email (optional)"         "$BUSINESS_EMAIL"
    prompt BUSINESS_WEBSITE  "Business website (optional)"       "$BUSINESS_WEBSITE"
    echo ""
    echo "--- First source (the consumer-site identity, NOT bootstrap) ---"
    prompt FIRST_SOURCE_CODE   "First source code (slug, e.g. my_business_website)" "$FIRST_SOURCE_CODE"
    prompt FIRST_SOURCE_NAME   "First source display name"     "$FIRST_SOURCE_NAME"
    prompt FIRST_SOURCE_DOMAIN "First source domain (e.g. mybusiness.com)" "$FIRST_SOURCE_DOMAIN"
    prompt FIRST_SOURCE_TYPE   "First source type (website / webhook / mcp / other)" "$FIRST_SOURCE_TYPE"
    echo ""
    prompt SDK_LANG "SDK languages to generate (all/python/php/typescript/none)" "$SDK_LANG"
    echo ""
fi

# ============================================================
# Validate required fields
# ============================================================
if [[ -z "$BUSINESS_NAME" ]]; then
    fail "--business-name is required (sets the business_settings.business_name NOT NULL field)."
fi
if [[ -z "$FIRST_SOURCE_CODE" || "$FIRST_SOURCE_CODE" == "bootstrap" ]]; then
    fail "--first-source-code must be set to a per-business slug (e.g. ${BUSINESS_NAME// /_}_website). Using 'bootstrap' as a runtime identity is forbidden — see docs/Sources.rst."
fi
if [[ -z "$FIRST_SOURCE_NAME" ]]; then
    FIRST_SOURCE_NAME="$BUSINESS_NAME Website"  # sensible default
fi

# ============================================================
# Install prerequisites
# ============================================================
# DNS pre-flight check (5b)
# ============================================================
if [[ -n "$DOMAIN" ]]; then
    log "Checking DNS for $DOMAIN..."
    apt-get install -y -qq dnsutils >/dev/null 2>&1 || true
    my_ip=$(curl -sf https://api.ipify.org 2>/dev/null || echo "")
    resolved=$(dig +short A "$DOMAIN" 2>/dev/null | head -1 || echo "")
    if [[ -n "$my_ip" && -n "$resolved" ]]; then
        if [[ "$my_ip" != "$resolved" ]]; then
            warn "Domain $DOMAIN resolves to $resolved but this host is $my_ip. Caddy TLS will likely fail."
        else
            log "DNS OK: $DOMAIN -> $my_ip"
        fi
    else
        warn "Could not verify DNS for $DOMAIN — proceeding, but Caddy may fail to get a cert"
    fi
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

# Only create log dir + parent before clone. $INSTALL_DIR itself and
# its backups/ subdir are created AFTER the clone — git clone refuses
# to clone into a non-empty directory, so we must not pre-create them.
mkdir -p /var/log/client-hub
chown clienthub:clienthub /var/log/client-hub
chmod 0750 /var/log/client-hub

# ============================================================
# Download source
# ============================================================
if [[ -n "${CLIENTHUB_TARBALL_URL:-}" ]]; then
    log "Downloading from tarball: $CLIENTHUB_TARBALL_URL"
    mkdir -p "$INSTALL_DIR"
    curl -fsSL "$CLIENTHUB_TARBALL_URL" | tar -xz -C "$INSTALL_DIR" --strip-components=1
else
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        log "Updating existing repo..."
        cd "$INSTALL_DIR" && git pull --ff-only
    elif [[ -d "$INSTALL_DIR" ]]; then
        # Directory exists but is not a git clone — fail loudly so we
        # don't accidentally clobber someone's files.
        fail "$INSTALL_DIR exists but is not a git repo. Remove it and re-run, or use --install-dir."
    else
        log "Cloning repository..."
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
fi

# Now that source is in place, create auxiliary dirs and set ownership
mkdir -p "$INSTALL_DIR/backups"
chown -R clienthub:clienthub "$INSTALL_DIR"
chmod 0750 "$INSTALL_DIR"
chmod 0700 "$INSTALL_DIR/backups"

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

# Brief pause — MariaDB can respond to ping before it's fully ready for piped SQL
sleep 3

# ============================================================
# Run migrations (via bootstrap-migrations.sh)
# ============================================================
log "Running migrations..."

# Helper: write a partial install summary so credentials are never lost
write_partial_summary() {
    local reason="$1"
    if [[ -n "$DOMAIN" ]]; then
        API_URL_DISPLAY="https://$DOMAIN"
    else
        API_URL_DISPLAY="http://$(hostname -I | awk '{print $1}'):8800"
    fi
    local PARTIAL_SUMMARY="=====================================================
Client Hub Installation INCOMPLETE — $reason
=====================================================

Install path:  $INSTALL_DIR
Mode:          $MODE
Domain:        ${DOMAIN:-none (plain HTTP on port 8800)}
API URL:       $API_URL_DISPLAY

Credentials (SAVE THESE — installation can be retried):

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

To retry: cd $INSTALL_DIR && ./scripts/install.sh (or re-run the curl installer)
====================================================="
    echo "$PARTIAL_SUMMARY" | tee "$INSTALL_DIR/.install-summary"
    chown clienthub:clienthub "$INSTALL_DIR/.install-summary" 2>/dev/null || true
    chmod 0600 "$INSTALL_DIR/.install-summary" 2>/dev/null || true
}

# Helper for SQL inside the container
run_sql() {
    docker compose -f "$COMPOSE_FILE" exec -T mariadb \
        mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub -e "$1" 2>&1
}

SEED_FLAG=""
if $INCLUDE_SEED_DATA; then
    SEED_FLAG="--with-seed-data"
fi

# Use the containerized mariadb client for migrations
chmod +x "$INSTALL_DIR/scripts/bootstrap-migrations.sh"

# Create tracking table first (the runner does this too, but belt-and-suspenders)
run_sql "CREATE TABLE IF NOT EXISTS _schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"

# Apply schema migrations
for migration_file in migrations/*.sql; do
    version=$(basename "$migration_file")
    already=$(run_sql "SELECT COUNT(*) FROM _schema_migrations WHERE version = '${version}';" | tail -1 | tr -d '[:space:]')
    if [[ "$already" -gt 0 ]]; then
        continue
    fi
    log "  Applying: $version"
    if ! docker compose -f "$COMPOSE_FILE" exec -T mariadb \
        mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub < "$migration_file" 2>&1; then
        write_partial_summary "Migration failed: $version"
        fail "Migration failed: $version — credentials saved to $INSTALL_DIR/.install-summary"
    fi
    run_sql "INSERT INTO _schema_migrations (version) VALUES ('${version}');"
done

# Apply dev seed data only if explicitly requested
if $INCLUDE_SEED_DATA && [[ -d "migrations/dev" ]]; then
    log "  Including seed data (--include-seed-data)..."
    for migration_file in migrations/dev/*.sql; do
        version="dev/$(basename "$migration_file")"
        already=$(run_sql "SELECT COUNT(*) FROM _schema_migrations WHERE version = '${version}';" | tail -1 | tr -d '[:space:]')
        if [[ "$already" -gt 0 ]]; then
            continue
        fi
        log "  Applying: $version"
        if ! docker compose -f "$COMPOSE_FILE" exec -T mariadb \
            mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub < "$migration_file" 2>&1; then
            write_partial_summary "Dev seed migration failed: $version"
            fail "Migration failed: $version — credentials saved to $INSTALL_DIR/.install-summary"
        fi
        run_sql "INSERT INTO _schema_migrations (version) VALUES ('${version}');"
    done
fi

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

# Create the named source. The seeded ``bootstrap`` row is left in
# place by the migrations but never used as a runtime identity. The
# named row carries the consumer-site domain so the marketing-source
# derivation can authoritatively classify same-domain referrers.
SOURCE_PAYLOAD=$(python3 -c "
import json,sys
p = {'code': '${FIRST_SOURCE_CODE}',
     'name': '${FIRST_SOURCE_NAME}',
     'source_type': '${FIRST_SOURCE_TYPE}'}
if '${FIRST_SOURCE_DOMAIN}':
    p['domain'] = '${FIRST_SOURCE_DOMAIN}'
print(json.dumps(p))
")
curl -sf -X POST \
    -H "X-API-Key: $CLIENTHUB_ROOT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$SOURCE_PAYLOAD" \
    http://127.0.0.1:8800/api/v1/admin/sources >/dev/null \
    || fail "Failed to create source ${FIRST_SOURCE_CODE}"

FIRST_SOURCE_UUID=$(curl -sf -H "X-API-Key: $CLIENTHUB_ROOT_API_KEY" \
    http://127.0.0.1:8800/api/v1/admin/sources \
    | python3 -c "import sys,json; sources=json.load(sys.stdin)['data']; print(next(s['uuid'] for s in sources if s['code']=='$FIRST_SOURCE_CODE'))")

# Insert API key directly into DB (we have the pre-generated key)
KEY_PREFIX="${FIRST_SOURCE_API_KEY:0:8}"
run_sql "INSERT INTO api_keys (uuid, source_id, key_prefix, key_value, name)
SELECT UUID(), s.id, '${KEY_PREFIX}', '${FIRST_SOURCE_API_KEY}', 'Install-generated key'
FROM sources s WHERE s.code = '${FIRST_SOURCE_CODE}';"

# ============================================================
# Populate business_settings (the singleton describing the business
# that owns this Client Hub instance). This is what every install
# should have been doing all along — earlier installs left the table
# empty, which is now treated as a deployment defect.
# Built with a Python helper so values containing quotes or
# specials are escaped correctly into the SQL literal.
# ============================================================
log "Populating business_settings..."
BUSINESS_INSERT_SQL=$(BIZ_NAME="$BUSINESS_NAME" \
                      BIZ_TYPE="$BUSINESS_TYPE" \
                      BIZ_TZ="$BUSINESS_TIMEZONE" \
                      BIZ_CUR="$BUSINESS_CURRENCY" \
                      BIZ_CTRY="$BUSINESS_COUNTRY" \
                      BIZ_PHONE="$BUSINESS_PHONE" \
                      BIZ_EMAIL="$BUSINESS_EMAIL" \
                      BIZ_WEB="$BUSINESS_WEBSITE" \
                      python3 - <<'PYEOF'
import os
def q(v):
    if v is None or v == "":
        return "NULL"
    return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
sql = (
    "INSERT INTO business_settings "
    "(business_name, business_type, timezone, currency, country, "
    "phone, email, website) VALUES ("
    f"{q(os.environ['BIZ_NAME'])}, "
    f"{q(os.environ.get('BIZ_TYPE'))}, "
    f"{q(os.environ['BIZ_TZ'])}, "
    f"{q(os.environ['BIZ_CUR'])}, "
    f"{q(os.environ['BIZ_CTRY'])}, "
    f"{q(os.environ.get('BIZ_PHONE'))}, "
    f"{q(os.environ.get('BIZ_EMAIL'))}, "
    f"{q(os.environ.get('BIZ_WEB'))})"
)
print(sql)
PYEOF
)
run_sql "$BUSINESS_INSERT_SQL" >/dev/null \
    || warn "business_settings insert failed (continuing) — populate manually if needed"

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
