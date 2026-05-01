#!/usr/bin/env bash
# generate-sdks.sh — Auto-generate Client Hub SDKs from OpenAPI spec
#
# Usage:
#   ./scripts/generate-sdks.sh           # Generate all SDKs
#   ./scripts/generate-sdks.sh python    # Generate Python SDK only
#   ./scripts/generate-sdks.sh php       # Generate PHP SDK only
#   ./scripts/generate-sdks.sh typescript # Generate TypeScript SDK only
#
# Prerequisites:
#   - Docker (uses openapitools/openapi-generator-cli image)
#   - Client Hub API running on port 8800

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SDK_DIR="$PROJECT_DIR/sdks"
SPEC_FILE="$SDK_DIR/openapi.json"
API_URL="${CLIENT_HUB_API_URL:-http://10.0.1.220:8800}"
GENERATOR_IMAGE="openapitools/openapi-generator-cli:v7.12.0"
LANGUAGE="${1:-all}"

# Single source of truth for SDK package versions — same file FastAPI reads.
VERSION_FILE="$PROJECT_DIR/api/VERSION"
if [[ -f "$VERSION_FILE" ]]; then
    PACKAGE_VERSION="$(tr -d ' \t\n\r' < "$VERSION_FILE")"
else
    PACKAGE_VERSION="0.0.0"
fi

# Resolve current uid:gid so the generator container writes files we own.
# (Older runs that wrote root-owned files can be normalized in one step
# with: docker run --rm -v "$SDK_DIR:/work" alpine chown -R "$(id -u):$(id -g)" /work)
HOST_UID="$(id -u)"
HOST_GID="$(id -g)"

echo "=== Client Hub SDK Generator ==="
echo "API URL: $API_URL"
echo "SDK dir: $SDK_DIR"
echo "Version: $PACKAGE_VERSION"
echo ""

# Step 1: Fetch OpenAPI spec
echo "Fetching OpenAPI spec from $API_URL/openapi.json ..."
mkdir -p "$SDK_DIR"
curl -sf "$API_URL/openapi.json" -o "$SPEC_FILE"
echo "  Saved to $SPEC_FILE"
echo ""

generate_sdk() {
    local lang="$1"
    local generator="$2"
    local output_dir="$SDK_DIR/$lang"
    local extra_args="${3:-}"

    echo "Generating $lang SDK (v$PACKAGE_VERSION)..."
    rm -rf "$output_dir"
    mkdir -p "$output_dir"

    docker run --rm \
        --user "$HOST_UID:$HOST_GID" \
        -v "$SDK_DIR:/sdk" \
        "$GENERATOR_IMAGE" generate \
        -i "/sdk/openapi.json" \
        -g "$generator" \
        -o "/sdk/$lang" \
        --package-name clienthub \
        --additional-properties=projectName=clienthub,packageVersion=$PACKAGE_VERSION \
        $extra_args \
        2>&1 | tail -5

    echo "  Generated: $output_dir"
    echo ""
}

# Step 2: Generate SDKs
if [[ "$LANGUAGE" == "all" || "$LANGUAGE" == "python" ]]; then
    generate_sdk "python" "python" "--additional-properties=packageName=clienthub,projectName=clienthub"
fi

if [[ "$LANGUAGE" == "all" || "$LANGUAGE" == "php" ]]; then
    generate_sdk "php" "php" "--additional-properties=packageName=ClientHub,invokerPackage=ClientHub"
fi

if [[ "$LANGUAGE" == "all" || "$LANGUAGE" == "typescript" ]]; then
    generate_sdk "typescript" "typescript-fetch" "--additional-properties=npmName=clienthub,supportsES6=true"
fi

echo "=== Done ==="
echo "SDKs generated in: $SDK_DIR/"
ls -d "$SDK_DIR"/*/ 2>/dev/null || echo "  (no SDKs generated)"
