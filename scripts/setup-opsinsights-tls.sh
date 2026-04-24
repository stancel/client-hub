#!/usr/bin/env bash
# setup-opsinsights-tls.sh
#
# Configure a Client Hub VPS to accept direct MySQL-over-TLS connections
# from the OpsInsights SaaS dashboard backend, restricted by IP allowlist.
#
# What this does, in order:
#   1. Adds a second site block to the Caddyfile for the supplied hostname,
#      reloads Caddy, and waits for it to acquire a Let's Encrypt cert
#      via ACME HTTP-01.
#   2. Copies the issued cert + key to ./data/mariadb-tls/ with UID/GID
#      999:999 (the mysql user inside the MariaDB container).
#   3. Patches docker-compose.bundled.yml (backed up first) to:
#         - publish MariaDB on 3306
#         - bind-mount the cert dir into the container read-only
#         - pass --ssl-cert and --ssl-key as server command args
#      Global --require-secure-transport is intentionally NOT set because
#      it would break the internal FastAPI container's plain-TCP connection;
#      TLS is enforced per-user instead.
#   4. Installs iptables-persistent and adds rules to the DOCKER-USER chain
#      to allow inbound 3306 only from the supplied --allow-ip addresses;
#      all other sources are DROPped. IPv6 gets a blanket DROP on 3306.
#   5. Recreates the MariaDB container to pick up the compose changes.
#   6. Creates (or rotates with --rotate-password) a read-only MariaDB user
#      'opsinsights_ro' with SELECT on ${DB_NAME} and REQUIRE SSL. The
#      OpsInsights ADOdb PDO SSL bug was fixed and deployed to production on
#      2026-04-18 and verified end-to-end against the Clever Orchid Client
#      Hub, so REQUIRE SSL is now the default. Pass --no-require-ssl ONLY if
#      you're onboarding against an OpsInsights environment that doesn't yet
#      have the ADOdb patch deployed.
#   7. Writes the credentials to ./data/opsinsights_credentials.txt (0600,
#      root) and prints them to stdout.
#
# Safe to re-run: steps are idempotent. Re-running without --rotate-password
# will refresh the cert copy and verify the user exists but will NOT change
# the password. Use --rotate-password to generate a new one.
#
# Usage:
#   sudo ./setup-opsinsights-tls.sh \
#        --hostname client-hub.customer.com \
#        --allow-ip 52.72.248.4 \
#        --allow-ip 52.207.33.249
#
# Optional:
#   --install-dir /opt/client-hub       (default shown)
#   --mariadb-user opsinsights_ro       (default)
#   --no-require-ssl                    (skip the REQUIRE SSL clause on the
#                                        user — only use if the target
#                                        OpsInsights environment is on a
#                                        build that predates the 2026-04-18
#                                        ADOdb PDO SSL fix)
#   --rotate-password                   (generate a new password even if
#                                        the user already exists)
#   --dry-run                           (print what would happen, change
#                                        nothing)
#   --non-interactive                   (no prompts — fail instead)

set -euo pipefail

# ============================================================
# Defaults
# ============================================================
INSTALL_DIR="/opt/client-hub"
HOSTNAME=""
ALLOW_IPS=()
MARIADB_USER="opsinsights_ro"
REQUIRE_SSL=true
ROTATE_PASSWORD=false
DRY_RUN=false
NON_INTERACTIVE=false

# ============================================================
# Helpers
# ============================================================
log()  { echo "[setup-opsinsights-tls] $*"; }
warn() { echo "[setup-opsinsights-tls] WARNING: $*" >&2; }
fail() { echo "[setup-opsinsights-tls] FATAL: $*" >&2; exit 1; }

run() {
    if $DRY_RUN; then
        echo "[dry-run] $*"
    else
        eval "$@"
    fi
}

usage() {
    sed -n '2,/^$/p' "$0" | sed 's/^# //;s/^#//'
    exit "${1:-0}"
}

# ============================================================
# Parse args
# ============================================================
while [[ $# -gt 0 ]]; do
    case "$1" in
        --hostname)          HOSTNAME="$2"; shift 2 ;;
        --allow-ip)          ALLOW_IPS+=("$2"); shift 2 ;;
        --install-dir)       INSTALL_DIR="$2"; shift 2 ;;
        --mariadb-user)      MARIADB_USER="$2"; shift 2 ;;
        --require-ssl)       REQUIRE_SSL=true; shift ;;   # back-compat: still accepted
        --no-require-ssl)    REQUIRE_SSL=false; shift ;;
        --rotate-password)   ROTATE_PASSWORD=true; shift ;;
        --dry-run)           DRY_RUN=true; shift ;;
        --non-interactive)   NON_INTERACTIVE=true; shift ;;
        -h|--help)           usage 0 ;;
        *)                   echo "Unknown option: $1"; usage 1 ;;
    esac
done

# ============================================================
# Pre-flight checks
# ============================================================
log "=== Pre-flight checks ==="

[[ "$(id -u)" -eq 0 ]] || fail "Must run as root (sudo)."
[[ -n "$HOSTNAME" ]] || fail "--hostname is required."
[[ ${#ALLOW_IPS[@]} -gt 0 ]] || fail "At least one --allow-ip is required."
[[ -d "$INSTALL_DIR" ]] || fail "Install dir $INSTALL_DIR does not exist."
[[ -f "$INSTALL_DIR/.env" ]] || fail "$INSTALL_DIR/.env is missing."
[[ -f "$INSTALL_DIR/docker-compose.bundled.yml" ]] \
    || fail "$INSTALL_DIR/docker-compose.bundled.yml is missing."
[[ -f "$INSTALL_DIR/Caddyfile" ]] || fail "$INSTALL_DIR/Caddyfile is missing."

command -v docker >/dev/null || fail "docker is not installed."
docker compose version >/dev/null 2>&1 || fail "docker compose plugin is required."
docker ps --format '{{.Names}}' | grep -q '^clienthub-mariadb$' \
    || fail "clienthub-mariadb container is not running. Run docker compose up -d first."
docker ps --format '{{.Names}}' | grep -q '^clienthub-caddy$' \
    || fail "clienthub-caddy container is not running. Run docker compose up -d first."

# Validate IPv4 format for allow-ips
for ip in "${ALLOW_IPS[@]}"; do
    [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || fail "Invalid IP: $ip"
done

# Hostname DNS must resolve to THIS host (so Let's Encrypt HTTP-01 works)
MY_PUBLIC_IP=$(curl -s --max-time 5 https://api.ipify.org || echo "")
HOSTNAME_IP=$(dig +short "$HOSTNAME" A | head -1)
if [[ -z "$HOSTNAME_IP" ]]; then
    warn "$HOSTNAME has no A record — Caddy will fail to get a cert."
    $NON_INTERACTIVE && fail "Aborting in non-interactive mode."
    read -rp "Continue anyway? [y/N]: " yn
    [[ "$yn" =~ ^[Yy]$ ]] || exit 1
elif [[ -n "$MY_PUBLIC_IP" && "$HOSTNAME_IP" != "$MY_PUBLIC_IP" ]]; then
    warn "$HOSTNAME resolves to $HOSTNAME_IP but this host is $MY_PUBLIC_IP."
    warn "Let's Encrypt HTTP-01 challenge will fail until DNS is fixed."
    $NON_INTERACTIVE && fail "Aborting in non-interactive mode."
    read -rp "Continue anyway? [y/N]: " yn
    [[ "$yn" =~ ^[Yy]$ ]] || exit 1
fi

log "Hostname:       $HOSTNAME (resolves to $HOSTNAME_IP)"
log "This host:      $MY_PUBLIC_IP"
log "Allow IPs:      ${ALLOW_IPS[*]}"
log "Install dir:    $INSTALL_DIR"
log "MariaDB user:   $MARIADB_USER"
log "Rotate passwd:  $ROTATE_PASSWORD"
log "Dry run:        $DRY_RUN"
$DRY_RUN && log "--- DRY RUN: no changes will be made ---"

cd "$INSTALL_DIR"

# Load DB_NAME and MARIADB_ROOT_PASSWORD from .env
# shellcheck disable=SC2046
set -a
# shellcheck disable=SC1091
source <(grep -E '^(DB_NAME|MARIADB_ROOT_PASSWORD)=' .env)
set +a
DB_NAME="${DB_NAME:-clienthub}"
[[ -n "${MARIADB_ROOT_PASSWORD:-}" ]] \
    || fail "MARIADB_ROOT_PASSWORD not found in .env"

# ============================================================
# Step 1: Caddyfile — ensure Caddy is serving HOSTNAME with a cert
# ============================================================
log
log "=== Step 1: Caddyfile ==="

# Three ways a Caddy install can already be serving this hostname:
#   (a) literal "HOSTNAME {" block in Caddyfile (explicit vhost),
#   (b) "{\$DOMAIN} {" template block + DOMAIN env var set to HOSTNAME,
#   (c) some other Caddy config that's already produced an LE cert.
# All three cases leave a populated cert directory under ./data/caddy.
# If the cert is already there we don't need to touch Caddyfile; the
# rest of this script only needs the cert file path.
EXISTING_CERT="$INSTALL_DIR/data/caddy/caddy/certificates/acme-v02.api.letsencrypt.org-directory/$HOSTNAME/$HOSTNAME.crt"

if [[ -f "$EXISTING_CERT" ]]; then
    log "Cert already issued for $HOSTNAME at $EXISTING_CERT — skipping Caddyfile step."
elif grep -qF "$HOSTNAME {" Caddyfile; then
    log "Hostname block already present in Caddyfile but cert not yet issued."
    log "Reloading Caddy to retrigger cert issuance..."
    run "docker exec clienthub-caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile"
    log "Waiting 25s for Let's Encrypt HTTP-01 to complete..."
    $DRY_RUN || sleep 25
else
    log "Backing up Caddyfile and appending new site block..."
    run "cp -n Caddyfile Caddyfile.bak-pre-opsinsights"
    run "cat >> Caddyfile <<CADDYEOF

$HOSTNAME {
    encode gzip

    reverse_proxy client-hub-api:8800

    log {
        output file /var/log/caddy/access.log
        format json
    }
}
CADDYEOF"

    log "Reloading Caddy..."
    run "docker exec clienthub-caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile"

    log "Waiting 25s for Let's Encrypt HTTP-01 to complete..."
    $DRY_RUN || sleep 25
fi

# ============================================================
# Step 2: Copy cert to mariadb-tls dir
# ============================================================
log
log "=== Step 2: Stage cert for MariaDB ==="

CERT_SRC="$INSTALL_DIR/data/caddy/caddy/certificates/acme-v02.api.letsencrypt.org-directory/$HOSTNAME"

if ! $DRY_RUN; then
    if [[ ! -f "$CERT_SRC/$HOSTNAME.crt" ]]; then
        fail "Cert not found at $CERT_SRC/$HOSTNAME.crt. Check Caddy logs: docker logs clienthub-caddy"
    fi
fi

run "mkdir -p $INSTALL_DIR/data/mariadb-tls"
run "cp $CERT_SRC/$HOSTNAME.crt $INSTALL_DIR/data/mariadb-tls/server.crt"
run "cp $CERT_SRC/$HOSTNAME.key $INSTALL_DIR/data/mariadb-tls/server.key"
run "chown -R 999:999 $INSTALL_DIR/data/mariadb-tls"
run "chmod 750 $INSTALL_DIR/data/mariadb-tls"
run "chmod 640 $INSTALL_DIR/data/mariadb-tls/server.crt"
run "chmod 600 $INSTALL_DIR/data/mariadb-tls/server.key"

log "Cert subject:"
if ! $DRY_RUN; then
    openssl x509 -in "$INSTALL_DIR/data/mariadb-tls/server.crt" -noout -subject -issuer -dates
fi

# ============================================================
# Step 3: Write docker-compose.opsinsights.yml override
# ============================================================
# We used to patch docker-compose.bundled.yml in place, which is a
# git-tracked file — so any `git pull` or `git reset --hard` silently
# reverted the OpsInsights plumbing and broke the connection. Now we
# write a separate override file that Docker Compose merges onto the
# base. The override is gitignored, so upgrades never touch it.
log
log "=== Step 3: docker-compose.opsinsights.yml override ==="

LEGACY_MARKER="# OpsInsights TLS exposure via setup-opsinsights-tls.sh"
OVERRIDE_FILE="$INSTALL_DIR/docker-compose.opsinsights.yml"

# Migration: if the base compose still carries the old in-place patches
# (installs set up before this refactor), revert them first. The patches
# are exactly the same fields the override file will provide, so without
# reverting we'd get duplicate port bindings etc.
if grep -qF "$LEGACY_MARKER" "$INSTALL_DIR/docker-compose.bundled.yml"; then
    log "Legacy in-place patches detected on docker-compose.bundled.yml — reverting."
    if [[ -f "$INSTALL_DIR/docker-compose.bundled.yml.bak-pre-opsinsights" ]]; then
        run "cp $INSTALL_DIR/docker-compose.bundled.yml.bak-pre-opsinsights $INSTALL_DIR/docker-compose.bundled.yml"
        log "  Restored from .bak-pre-opsinsights."
    elif (cd "$INSTALL_DIR" && git ls-files --error-unmatch docker-compose.bundled.yml >/dev/null 2>&1); then
        run "git -C $INSTALL_DIR checkout -- docker-compose.bundled.yml"
        log "  Restored from git (the .bak file was lost to a prior git reset)."
    else
        warn "Could not auto-revert legacy patches — neither .bak nor git-tracked copy available. You may need to revert docker-compose.bundled.yml manually."
    fi
fi

if [[ -f "$OVERRIDE_FILE" ]] && ! $DRY_RUN; then
    log "Override file already exists — refreshing to current canonical form."
fi

run "cat > $OVERRIDE_FILE <<'OVRYAML'
# docker-compose.opsinsights.yml
#
# Override written by scripts/setup-opsinsights-tls.sh. Merged onto
# docker-compose.bundled.yml via docker compose -f bundled.yml -f opsinsights.yml.
# Adds MariaDB port publish, TLS cert mount, and --ssl-cert/--ssl-key flags.
#
# Gitignored — never committed. Delete + re-run setup-opsinsights-tls.sh to
# regenerate.

services:
  mariadb:
    ports:
      - \"3306:3306\"
    volumes:
      - ./data/mariadb-tls:/etc/mysql-tls:ro
    command:
      - --ssl-cert=/etc/mysql-tls/server.crt
      - --ssl-key=/etc/mysql-tls/server.key
OVRYAML"

run "chmod 0644 $OVERRIDE_FILE"

# Sanity — docker compose should be able to parse both files together.
if ! $DRY_RUN; then
    if ! (cd "$INSTALL_DIR" && docker compose -f docker-compose.bundled.yml -f docker-compose.opsinsights.yml config >/dev/null 2>&1); then
        fail "Merged compose config is invalid. Inspect with: docker compose -f docker-compose.bundled.yml -f docker-compose.opsinsights.yml config"
    fi
    log "Merged compose config parses cleanly."
fi

# ============================================================
# Step 4: iptables allowlist in DOCKER-USER chain
# ============================================================
log
log "=== Step 4: iptables allowlist ==="

# First ensure the DROP rule exists (so the chain isn't fully open if
# we re-run and the DROP is already there)
if ! iptables -C DOCKER-USER -p tcp --dport 3306 -j DROP 2>/dev/null; then
    run "iptables -I DOCKER-USER -p tcp --dport 3306 -j DROP"
else
    log "IPv4 DROP rule for 3306 already present."
fi

# Add ACCEPT rule for each allow IP (if not already there)
for ip in "${ALLOW_IPS[@]}"; do
    if ! iptables -C DOCKER-USER -p tcp --dport 3306 -s "$ip/32" -j ACCEPT 2>/dev/null; then
        run "iptables -I DOCKER-USER -p tcp --dport 3306 -s $ip/32 -j ACCEPT"
        log "Allowed $ip"
    else
        log "$ip already whitelisted."
    fi
done

# IPv6: blanket DROP (allowlist is IPv4-only)
if ! ip6tables -C DOCKER-USER -p tcp --dport 3306 -j DROP 2>/dev/null; then
    run "ip6tables -I DOCKER-USER -p tcp --dport 3306 -j DROP"
fi

log "DOCKER-USER chain (IPv4):"
$DRY_RUN || iptables -L DOCKER-USER -n --line-numbers

log "Installing iptables-persistent..."
# The `dpkg -l` check returns 0 even when a package is in the "un"
# (unknown/not-installed) state, so verify by checking for the actual
# binary instead. Once installed, fail loudly if the command still
# isn't on PATH — previously this silently fell through to a
# "netfilter-persistent: command not found" later on.
if ! command -v netfilter-persistent >/dev/null 2>&1; then
    run "echo iptables-persistent iptables-persistent/autosave_v4 boolean false | debconf-set-selections"
    run "echo iptables-persistent iptables-persistent/autosave_v6 boolean false | debconf-set-selections"
    run "DEBIAN_FRONTEND=noninteractive apt-get update -qq"
    run "DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent"
fi
if ! $DRY_RUN && ! command -v netfilter-persistent >/dev/null 2>&1; then
    fail "iptables-persistent install did not register netfilter-persistent on PATH. Try: sudo apt-get install iptables-persistent"
fi

run "netfilter-persistent save"

# ============================================================
# Step 5: Recreate MariaDB container
# ============================================================
log
log "=== Step 5: Apply compose changes ==="

# Force recreate so the override's ports + volumes + command take effect.
# Without --force-recreate, docker compose may see a running mariadb with
# the same env and skip the recreation even though the override file
# changed (ports/volumes/command are container-config, not env).
run "docker compose -f docker-compose.bundled.yml -f docker-compose.opsinsights.yml up -d --force-recreate mariadb"

log "Waiting 15s for MariaDB to become healthy..."
$DRY_RUN || sleep 15

if ! $DRY_RUN; then
    if ! docker ps --filter "name=clienthub-mariadb" --filter "health=healthy" -q | grep -q .; then
        docker ps --filter "name=clienthub-mariadb"
        fail "MariaDB did not become healthy. Check: docker logs clienthub-mariadb"
    fi
    log "MariaDB is healthy and listening on $(ss -tlnp 2>/dev/null | awk '/:3306/ {print $4}' | paste -sd,)."
fi

# ============================================================
# Step 6: Create/rotate MariaDB user
# ============================================================
log
log "=== Step 6: $MARIADB_USER user ==="

USER_EXISTS=0
if ! $DRY_RUN; then
    USER_EXISTS=$(docker exec -i clienthub-mariadb mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" \
        -sNe "SELECT COUNT(*) FROM mysql.user WHERE User='$MARIADB_USER' AND Host='%';" 2>/dev/null || echo 0)
fi

if [[ "$USER_EXISTS" -eq 0 ]] || $ROTATE_PASSWORD; then
    OPS_PASS=$(openssl rand -base64 30 | tr -d '/+=' | head -c 32)
    if $REQUIRE_SSL; then
        REQUIRE_CLAUSE="REQUIRE SSL"
        log "Creating/rotating user with new 32-char password and REQUIRE SSL."
    else
        REQUIRE_CLAUSE="REQUIRE NONE"
        log "Creating/rotating user with new 32-char password. REQUIRE SSL NOT set (--no-require-ssl passed) — only use this if the target OpsInsights environment predates the 2026-04-18 ADOdb PDO SSL fix. IP allowlist is the primary security boundary either way."
    fi

    if ! $DRY_RUN; then
        docker exec -i clienthub-mariadb mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" <<SQL
DROP USER IF EXISTS '$MARIADB_USER'@'%';
CREATE USER '$MARIADB_USER'@'%' IDENTIFIED BY '$OPS_PASS' $REQUIRE_CLAUSE;
GRANT SELECT ON $DB_NAME.* TO '$MARIADB_USER'@'%';
FLUSH PRIVILEGES;
SQL
    fi
else
    log "User $MARIADB_USER already exists and --rotate-password not given — keeping existing password."
    log "Current credentials are in $INSTALL_DIR/data/opsinsights_credentials.txt"
    OPS_PASS=""
fi

# ============================================================
# Step 7: Write credentials file (only if password changed)
# ============================================================
if [[ -n "$OPS_PASS" ]]; then
    log
    log "=== Step 7: Write credentials file ==="

    if ! $DRY_RUN; then
        umask 077
        cat > "$INSTALL_DIR/data/opsinsights_credentials.txt" <<EOF
OpsInsights -> Client Hub connection
Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Hostname:  $HOSTNAME

Host:      $HOSTNAME
Port:      3306
Database:  $DB_NAME
User:      $MARIADB_USER
Password:  $OPS_PASS
$(if $REQUIRE_SSL; then echo "SSL:       REQUIRED on user (Let's Encrypt cert, publicly trusted)"; else echo "SSL:       offered by server but NOT required on user (--no-require-ssl — OpsInsights env predates the 2026-04-18 ADOdb fix)"; fi)

Firewall whitelist (iptables DOCKER-USER):
$(for ip in "${ALLOW_IPS[@]}"; do echo "  $ip"; done)

URI:
  $(if $REQUIRE_SSL; then echo "mysql://$MARIADB_USER:$OPS_PASS@$HOSTNAME:3306/$DB_NAME?ssl-mode=REQUIRED"; else echo "mysql://$MARIADB_USER:$OPS_PASS@$HOSTNAME:3306/$DB_NAME"; fi)
EOF
        chmod 600 "$INSTALL_DIR/data/opsinsights_credentials.txt"
    fi
fi

# ============================================================
# Step 8: Verify end-to-end from inside the container
# ============================================================
log
log "=== Step 8: Verification ==="

if ! $DRY_RUN; then
    # TLS login always works (server offers TLS regardless of user REQUIRE)
    if [[ -n "$OPS_PASS" ]]; then
        docker exec clienthub-mariadb mariadb \
            -h127.0.0.1 -u"$MARIADB_USER" -p"$OPS_PASS" --ssl \
            "$DB_NAME" -e "SELECT COUNT(*) FROM contacts; STATUS;" \
            2>&1 | grep -E "contacts|Cipher in use" || warn "TLS test output unexpected"
    fi

    if [[ -n "$OPS_PASS" ]]; then
        if $REQUIRE_SSL; then
            # Non-TLS MUST be rejected when REQUIRE SSL is on
            if docker exec clienthub-mariadb mariadb \
                   -h127.0.0.1 --skip-ssl -u"$MARIADB_USER" -p"$OPS_PASS" \
                   "$DB_NAME" -e "SELECT 1;" 2>&1 | grep -q "Access denied"; then
                log "Non-TLS connection correctly rejected (REQUIRE SSL enforced)."
            else
                warn "Non-TLS connection was NOT rejected — REQUIRE SSL clause not working."
            fi
        else
            # Non-TLS should work when REQUIRE SSL is off (--no-require-ssl mode).
            # mariadb client prints "1\n1" for SELECT 1 (header + row); match either.
            if docker exec clienthub-mariadb mariadb \
                   -h127.0.0.1 --skip-ssl -u"$MARIADB_USER" -p"$OPS_PASS" \
                   "$DB_NAME" -e "SELECT 1;" 2>&1 | grep -qE "^1$"; then
                log "Non-TLS connection succeeded (--no-require-ssl mode)."
            else
                warn "Non-TLS connection failed unexpectedly — check MariaDB config."
            fi
        fi
    fi
fi

# ============================================================
# Done
# ============================================================
log
log "=========================================="
log "Setup complete."
log "=========================================="

if [[ -n "$OPS_PASS" ]]; then
    echo
    echo "PLUG INTO OPSINSIGHTS:"
    echo "  Host:     $HOSTNAME"
    echo "  Port:     3306"
    echo "  Database: $DB_NAME"
    echo "  User:     $MARIADB_USER"
    echo "  Password: $OPS_PASS"
    echo "  SSL:      required"
    echo
    echo "Credentials also saved (mode 0600) at:"
    echo "  $INSTALL_DIR/data/opsinsights_credentials.txt"
    echo
fi
