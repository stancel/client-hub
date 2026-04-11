#!/usr/bin/env bash
# smoke-test.sh — Post-install verification for Client Hub
# Tests that the API is healthy, the database is reachable,
# and basic operations work.
#
# Usage: ./scripts/smoke-test.sh [--url URL] [--api-key KEY]

set -euo pipefail

API_URL="${1:-http://127.0.0.1:8800}"
API_KEY="${2:-}"
TIMEOUT=30
passed=0
failed=0

# Parse named args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --url)     API_URL="$2"; shift 2 ;;
        --api-key) API_KEY="$2"; shift 2 ;;
        *) shift ;;
    esac
done

check() {
    local name="$1"
    local result="$2"
    if [[ "$result" == "pass" ]]; then
        echo "  [PASS] $name"
        passed=$((passed + 1))
    else
        echo "  [FAIL] $name"
        failed=$((failed + 1))
    fi
}

echo "=== Client Hub Smoke Test ==="
echo "URL: $API_URL"
echo ""

# 1. Health check
echo "Testing health endpoint..."
health_code=$(curl -sf -o /dev/null -w "%{http_code}" "$API_URL/api/v1/health" 2>/dev/null || echo "000")
check "GET /api/v1/health returns 200" "$([ "$health_code" = "200" ] && echo pass || echo fail)"

# 2. Health response has database connected
health_body=$(curl -sf "$API_URL/api/v1/health" 2>/dev/null || echo "{}")
db_status=$(echo "$health_body" | python3 -c "import sys,json; print(json.load(sys.stdin).get('database',''))" 2>/dev/null || echo "")
check "Database is connected" "$([ "$db_status" = "connected" ] && echo pass || echo fail)"

# 3. OpenAPI spec available
spec_code=$(curl -sf -o /dev/null -w "%{http_code}" "$API_URL/openapi.json" 2>/dev/null || echo "000")
check "GET /openapi.json returns 200" "$([ "$spec_code" = "200" ] && echo pass || echo fail)"

# 4. Auth required on protected endpoints
unauth_code=$(curl -sf -o /dev/null -w "%{http_code}" "$API_URL/api/v1/contacts" 2>/dev/null || echo "000")
check "GET /contacts without key returns 401" "$([ "$unauth_code" = "401" ] && echo pass || echo fail)"

# 5. Authenticated access (if API key provided)
if [[ -n "$API_KEY" ]]; then
    auth_code=$(curl -sf -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/api/v1/contacts" 2>/dev/null || echo "000")
    check "GET /contacts with key returns 200" "$([ "$auth_code" = "200" ] && echo pass || echo fail)"

    settings_code=$(curl -sf -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/api/v1/settings" 2>/dev/null || echo "000")
    check "GET /settings with key returns 200" "$([ "$settings_code" = "200" ] && echo pass || echo fail)"

    sources_code=$(curl -sf -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/api/v1/admin/sources" 2>/dev/null || echo "000")
    check "GET /admin/sources with root key returns 200" "$([ "$sources_code" = "200" ] && echo pass || echo fail)"
fi

echo ""
echo "Results: $passed passed, $failed failed"

if [[ "$failed" -gt 0 ]]; then
    exit 1
fi
echo "All smoke tests passed!"
