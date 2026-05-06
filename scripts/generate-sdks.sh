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

    # Post-process the generated TypeScript SDK so it can be published
    # to the private @bradstancel registry as a real npm package.
    # The openapi-generator template ships a stock package.json with
    # placeholder repo URL and an .npmignore that excludes README.md;
    # we override both, and replace the misleading auto-generated
    # README with one pointing at the actual private registry.
    ts_dir="$SDK_DIR/typescript"

    # Note: openapi-generator's typescript-fetch template ignores
    # --additional-properties=packageVersion (a known generator quirk —
    # python honors it, typescript-fetch does not). We force the
    # canonical version in via this jq merge so the published SDK
    # always matches api/VERSION. publish-sdk.yml CI verifies the git
    # tag matches this field, so a mismatch would block release.
    jq --arg pkg_version "$PACKAGE_VERSION" '. + {
        name: "@bradstancel/clienthub-sdk",
        version: $pkg_version,
        description: "TypeScript SDK for the Client Hub data-first customer intelligence API. Auto-generated from the OpenAPI spec on every release; do not edit by hand.",
        author: "Brad Stancel <brad@processfast.com>",
        license: "UNLICENSED",
        repository: {
            type: "git",
            url: "git+ssh://git@github.com/stancel/client-hub.git"
        },
        homepage: "https://github.com/stancel/client-hub#readme",
        publishConfig: {
            registry: "https://npm.onlinesalessystems.com/",
            access: "restricted"
        },
        files: ["dist", "README.md"],
        scripts: (.scripts + {prepublishOnly: "npm run build"})
    }' "$ts_dir/package.json" > "$ts_dir/package.json.tmp"
    mv "$ts_dir/package.json.tmp" "$ts_dir/package.json"

    # Stock .npmignore excludes README.md — wipe it so npm uses the
    # `files` allowlist from package.json instead.
    rm -f "$ts_dir/.npmignore"

    cat > "$ts_dir/README.md" <<'README_EOF'
# @bradstancel/clienthub-sdk

TypeScript SDK for the [Client Hub](https://github.com/stancel/client-hub)
data-first customer intelligence API.

> Auto-generated from the OpenAPI spec on every Client Hub release.
> **Do not edit by hand** — changes are clobbered on the next
> `./scripts/generate-sdks.sh` run.

## Install

The package is published to a private registry
(`https://npm.onlinesalessystems.com/`) under the `@bradstancel`
scope. Configure your project's `.npmrc` once:

```
@bradstancel:registry=https://npm.onlinesalessystems.com/
//npm.onlinesalessystems.com/:_authToken=${NPM_TOKEN}
```

Set `NPM_TOKEN` in your environment (the read-only `consumer` token
is sufficient for installs). Then:

```bash
npm install @bradstancel/clienthub-sdk
```

## Versioning

The SDK version always matches the Client Hub API version it was
generated against. `^0.3.5` will pull the latest `0.3.x` patch
release. Every Client Hub release tags `vX.Y.Z` in git and publishes
that exact version here via GitHub Actions.

## Quick start

```typescript
import { Configuration, ContactsApi } from '@bradstancel/clienthub-sdk';

const config = new Configuration({
  basePath: 'https://your-clienthub-instance.example.com',
  apiKey: () => process.env.CLIENT_HUB_API_KEY ?? '',
});

const contacts = new ContactsApi(config);
const result = await contacts.listContacts();
```

See your Client Hub instance's `/docs` URL for the full endpoint
surface (Swagger UI auto-generated from the same spec this SDK was
built from).

## Timeouts and cancellation

Every generated method takes an optional second argument
`initOverrides` whose contents are spread into the underlying
`fetch()` `RequestInit`. Pass an `AbortSignal` to apply a timeout
or cancellation:

```typescript
const controller = new AbortController();
const timer = setTimeout(() => controller.abort(), 3000);

try {
  await contacts.createContactEndpointApiV1ContactsPost(
    { contactCreate: { contactType: 'lead', emails: [{ address: 'x@y' }] } },
    { signal: controller.signal },
  );
} finally {
  clearTimeout(timer);
}
```

Any standard `fetch` option works the same way (`cache`,
`credentials`, custom `headers`, etc.) — just pass it inside the
`initOverrides` object.

## Source

- Project: <https://github.com/stancel/client-hub>
- Generator: `openapitools/openapi-generator-cli` (`typescript-fetch`)
- Spec source: `sdks/openapi.json` in the Client Hub repo
README_EOF

    echo "  Patched: $ts_dir/package.json (name, version, repo, publishConfig)"
    echo "  Removed: $ts_dir/.npmignore (was excluding README.md)"
    echo "  Wrote:   $ts_dir/README.md (private-registry install instructions)"
    echo ""
fi

echo "=== Done ==="
echo "SDKs generated in: $SDK_DIR/"
ls -d "$SDK_DIR"/*/ 2>/dev/null || echo "  (no SDKs generated)"
