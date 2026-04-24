#!/usr/bin/env bash
# uninstall.sh — Remove Client Hub installation
# Preserves backups by default. Use --purge to remove everything.
#
# Usage: sudo ./scripts/uninstall.sh [--purge]

set -euo pipefail

INSTALL_DIR="/opt/client-hub"
PURGE=false

if [[ "${1:-}" == "--purge" ]]; then
    PURGE=true
fi

if [[ "$(id -u)" -ne 0 ]]; then
    echo "Error: Must run as root (sudo)"
    exit 1
fi

echo "=== Client Hub Uninstaller ==="
echo ""

# Stop containers. Include the OpsInsights override if present so we
# tear down the exact same project that was running (container names,
# networks, and volumes all key off the merged compose).
stop_compose() {
    local base="$1"
    local args=(-f "$base")
    if [[ -f "$INSTALL_DIR/docker-compose.opsinsights.yml" ]]; then
        args+=(-f "$INSTALL_DIR/docker-compose.opsinsights.yml")
    fi
    docker compose "${args[@]}" down --remove-orphans 2>/dev/null || true
}

if [[ -f "$INSTALL_DIR/docker-compose.bundled.yml" ]]; then
    echo "Stopping containers..."
    stop_compose "$INSTALL_DIR/docker-compose.bundled.yml"
elif [[ -f "$INSTALL_DIR/docker-compose.bundled-nodomain.yml" ]]; then
    stop_compose "$INSTALL_DIR/docker-compose.bundled-nodomain.yml"
fi

# Remove cron job
if [[ -f /etc/cron.daily/client-hub-backup ]]; then
    echo "Removing backup cron job..."
    rm -f /etc/cron.daily/client-hub-backup
fi

# Remove log directory
if [[ -d /var/log/client-hub ]]; then
    echo "Removing log directory..."
    rm -rf /var/log/client-hub
fi

SAVED_DIR="/root/client-hub-saved"

if $PURGE; then
    echo "Purging all data including backups..."
    rm -rf "$INSTALL_DIR"
else
    # Preserve credentials and backups
    echo "Preserving credentials and backups..."
    mkdir -p "$SAVED_DIR"
    for f in .env .install-summary; do
        if [[ -f "$INSTALL_DIR/$f" ]]; then
            cp -p "$INSTALL_DIR/$f" "$SAVED_DIR/"
        fi
    done
    echo "  Credentials saved to $SAVED_DIR/"
    echo "  Backups preserved at $INSTALL_DIR/backups/"
    # Remove everything except backups
    find "$INSTALL_DIR" -mindepth 1 -maxdepth 1 ! -name 'backups' -exec rm -rf {} +
fi

# Remove system user (if exists and no processes running)
if id clienthub &>/dev/null; then
    echo "Removing clienthub system user..."
    userdel clienthub 2>/dev/null || true
fi

echo ""
if $PURGE; then
    echo "Client Hub fully purged."
else
    echo "Client Hub uninstalled. Backups preserved at $INSTALL_DIR/backups/"
fi
