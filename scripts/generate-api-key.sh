#!/usr/bin/env bash
# generate-api-key.sh — Create a new API key for a source
# Uses the admin API to create a new source-scoped API key.
#
# Usage: ./scripts/generate-api-key.sh --source-uuid UUID --name "Key Name"
#   --url URL          API URL (default: http://127.0.0.1:8800)
#   --root-key KEY     Root API key
#   --source-uuid UUID Source UUID to create key for
#   --name NAME        Key display name

set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8800}"
ROOT_KEY="${CLIENTHUB_ROOT_API_KEY:-}"
SOURCE_UUID=""
KEY_NAME="Default key"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --url)          API_URL="$2"; shift 2 ;;
        --root-key)     ROOT_KEY="$2"; shift 2 ;;
        --source-uuid)  SOURCE_UUID="$2"; shift 2 ;;
        --name)         KEY_NAME="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ -z "$ROOT_KEY" ]]; then
    echo "Error: --root-key or CLIENTHUB_ROOT_API_KEY required"
    exit 1
fi

if [[ -z "$SOURCE_UUID" ]]; then
    echo "Error: --source-uuid required"
    echo ""
    echo "Available sources:"
    curl -sf -H "X-API-Key: $ROOT_KEY" "$API_URL/api/v1/admin/sources" \
        | python3 -m json.tool
    exit 1
fi

echo "Creating API key for source $SOURCE_UUID..."
response=$(curl -sf -X POST \
    -H "X-API-Key: $ROOT_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$KEY_NAME\"}" \
    "$API_URL/api/v1/admin/sources/$SOURCE_UUID/api-keys")

echo "$response" | python3 -m json.tool

echo ""
echo "SAVE THE key_value ABOVE — it will not be shown again."
