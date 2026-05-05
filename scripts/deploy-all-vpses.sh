#!/usr/bin/env bash
# deploy-all-vpses.sh — Roll a Client Hub release to every production
# API VPS listed in deploy/vpses.txt.
#
# Sequential by default (safer): each VPS upgrade-and-verify must
# succeed before the next is touched. On any failure, prints the
# rollback hint already produced by upgrade.sh and aborts so the
# remaining VPSes are untouched.
#
# Usage:
#   ./scripts/deploy-all-vpses.sh                # interactive prompt before starting
#   ./scripts/deploy-all-vpses.sh --yes          # non-interactive (CI / scripting)
#   ./scripts/deploy-all-vpses.sh --hosts FILE   # alternate host list
#
# Each VPS is upgraded by:
#   ssh root@HOST 'cd /opt/client-hub && ./scripts/upgrade.sh --yes'
# Then verified by curling /api/v1/health and /openapi.json from
# Cybertron (proves both the bundled Caddy front-end and the API
# behind it came back).
#
# Exit codes:
#   0 — every VPS upgraded and verified
#   2 — usage / config error
#   3 — at least one VPS failed; remaining VPSes were skipped

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
HOSTS_FILE="$PROJECT_DIR/deploy/vpses.txt"
INTERACTIVE=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        --yes|-y)   INTERACTIVE=false; shift ;;
        --hosts)    HOSTS_FILE="$2"; shift 2 ;;
        -h|--help)  sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)          echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

if [[ ! -f "$HOSTS_FILE" ]]; then
    echo "Hosts file not found: $HOSTS_FILE" >&2
    exit 2
fi

mapfile -t HOSTS < <(grep -vE '^\s*(#|$)' "$HOSTS_FILE")
if [[ ${#HOSTS[@]} -eq 0 ]]; then
    echo "No hosts in $HOSTS_FILE" >&2
    exit 2
fi

if [[ -t 1 ]]; then
    C_BLUE='\033[1;34m'; C_GREEN='\033[1;32m'; C_RED='\033[1;31m'
    C_YELLOW='\033[1;33m'; C_DIM='\033[2m'; C_OFF='\033[0m'
else
    C_BLUE=''; C_GREEN=''; C_RED=''; C_YELLOW=''; C_DIM=''; C_OFF=''
fi

echo -e "${C_BLUE}=== Client Hub multi-VPS deployment ===${C_OFF}"
echo "Hosts file: $HOSTS_FILE"
echo "Hosts (${#HOSTS[@]}):"
for h in "${HOSTS[@]}"; do echo "  - $h"; done
echo

if $INTERACTIVE; then
    read -r -p "Proceed with sequential upgrade? [y/N] " ans
    case "$ans" in
        y|Y|yes|YES) ;;
        *) echo "Aborted."; exit 0 ;;
    esac
fi

declare -A PRE_HEAD POST_HEAD VERSION RESULT
OVERALL_RC=0

for host in "${HOSTS[@]}"; do
    echo
    echo -e "${C_BLUE}── $host ──${C_OFF}"

    # Capture pre-upgrade HEAD for the summary.
    PRE_HEAD["$host"]="$(ssh -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new \
        "root@$host" 'cd /opt/client-hub && git rev-parse --short HEAD' 2>/dev/null || echo '?')"

    # Run the canonical upgrade. Stream the script's output so the
    # operator can watch phase headers go by.
    if ssh -o ConnectTimeout=8 "root@$host" 'cd /opt/client-hub && ./scripts/upgrade.sh --yes'; then
        POST_HEAD["$host"]="$(ssh -o ConnectTimeout=8 "root@$host" \
            'cd /opt/client-hub && git rev-parse --short HEAD' 2>/dev/null || echo '?')"

        # Verify via the public TLS endpoint — proves Caddy + API both came back.
        health="$(curl -fsS --max-time 8 "https://$host/api/v1/health" 2>/dev/null || echo '')"
        version="$(curl -fsS --max-time 8 "https://$host/openapi.json" 2>/dev/null \
            | python3 -c 'import json,sys; print(json.load(sys.stdin)["info"]["version"])' 2>/dev/null || echo '?')"

        if [[ "$health" == *"\"status\":\"healthy\""* ]]; then
            VERSION["$host"]="$version"
            RESULT["$host"]="ok"
            echo -e "${C_GREEN}✓ $host upgraded to ${POST_HEAD[$host]} (v$version) — healthy${C_OFF}"
        else
            VERSION["$host"]="$version"
            RESULT["$host"]="health-check-failed"
            OVERALL_RC=3
            echo -e "${C_RED}✗ $host upgrade returned 0 but health check failed${C_OFF}"
            echo -e "${C_DIM}  raw health: $health${C_OFF}"
            echo -e "${C_YELLOW}  Aborting — remaining VPSes skipped.${C_OFF}"
            break
        fi
    else
        POST_HEAD["$host"]="?"
        VERSION["$host"]="?"
        RESULT["$host"]="upgrade-failed"
        OVERALL_RC=3
        echo -e "${C_RED}✗ $host upgrade failed (upgrade.sh non-zero exit)${C_OFF}"
        echo -e "${C_YELLOW}  See above for the rollback hint that upgrade.sh prints.${C_OFF}"
        echo -e "${C_YELLOW}  Aborting — remaining VPSes skipped.${C_OFF}"
        break
    fi
done

echo
echo -e "${C_BLUE}=== Summary ===${C_OFF}"
printf '%-58s %-10s %-10s %-8s %s\n' "HOST" "PRE-HEAD" "POST-HEAD" "VERSION" "RESULT"
for host in "${HOSTS[@]}"; do
    printf '%-58s %-10s %-10s %-8s %s\n' \
        "$host" \
        "${PRE_HEAD[$host]:-skip}" \
        "${POST_HEAD[$host]:-skip}" \
        "${VERSION[$host]:-skip}" \
        "${RESULT[$host]:-skip}"
done

if [[ $OVERALL_RC -eq 0 ]]; then
    echo -e "${C_GREEN}All VPSes upgraded and healthy.${C_OFF}"
else
    echo -e "${C_RED}Deployment incomplete. Investigate the failed host above.${C_OFF}"
fi
exit "$OVERALL_RC"
