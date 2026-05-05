# Client Hub v0.3.6 — Knowledge Transfer for Clever Orchid Website

**Audience:** the Claude Code session (or developer) working on the
**Clever Orchid Next.js consumer site** at
`/home/brad/Sites/clever-orchid-website` (master branch).

**Status:** Client Hub v0.3.6 is **already deployed** (commit
`4176b92`, both API VPSes healthy at `0.3.6`) and
`@bradstancel/clienthub-sdk@0.3.6` is **published** to
`https://npm.onlinesalessystems.com/`. Clever Orchid's existing
v0.3.5 SDK integration **keeps working unchanged** — v0.3.6 only
tightens types and adds quality gaps that align you with the new
canonical reference module. Adopting v0.3.6 is recommended, not
urgent.

## TL;DR

- Bump `@bradstancel/clienthub-sdk` to `^0.3.6` in `package.json`.
- Replace `lib/client-hub.ts` with the canonical reference module
  from
  `https://github.com/stancel/client-hub/blob/master/docs/Cross-Project-Integration.rst`
  (section *Reference Module: lib/client-hub.ts (SDK-based)*).
- Drop the `as { matches?: ...; count?: number }` cast on the
  `lookupEmailApiV1LookupEmailEmailGet` result in
  `appendCommunication` — the SDK now returns `Promise<LookupResponse>`
  with proper types. (The canonical already does this.)
- Test, commit, deploy on the standard CO VPS deploy procedure.

## What you specifically need to adopt from the canonical

Clever Orchid's v0.3.5 `lib/client-hub.ts` (commit `6524034`) is
structurally sound and contributed several patterns to the
canonical (lazy `apiKey: () => …`, cached `getClients()`). The
three things you need to pull in are CDC's contributions to the
synthesis:

### 1. `ResponseError` import + `readErrorBody()` helper

You currently log raw exceptions, which produces noisy logs when the
API returns an error:

```typescript
} catch (err) {
  console.warn("[client-hub] event failed:", err);
}
```

Replace with the parsed-error helper from the canonical so logs
include the HTTP status + first 200 chars of the response body:

```typescript
import {
  CommunicationsApi,
  Configuration,
  ContactsApi,
  LookupApi,
  ResponseError,  // <-- add this import
} from "@bradstancel/clienthub-sdk";

async function readErrorBody(err: unknown): Promise<string> {
  if (err instanceof ResponseError) {
    try {
      const text = await err.response.text();
      return `${err.response.status} ${text.slice(0, 200)}`;
    } catch {
      return `${err.response.status}`;
    }
  }
  return err instanceof Error ? err.message : String(err);
}

// Then in the catch blocks:
} catch (err) {
  console.warn("[client-hub] event failed:", await readErrorBody(err));
}
```

### 2. Extended UTM fields

Your current `LogConversionInput.utm` only has the standard 5
fields:

```typescript
utm?: {
  source?: string;
  medium?: string;
  campaign?: string;
  term?: string;
  content?: string;
};
```

The canonical extends this with first-touch metadata that paid
campaigns rely on:

```typescript
utm?: {
  source?: string;
  medium?: string;
  campaign?: string;
  term?: string;
  content?: string;
  gclid?: string;       // Google Click ID
  fbclid?: string;      // Facebook Click ID
  landing_page?: string; // first-touch landing page URL
  captured_at?: string;  // when the first-touch UTM was captured
};
```

Without these, any first-touch UTM data with `gclid` / `fbclid` is
silently dropped on its way through the type system (TypeScript
filters out unknown properties when the object is built from a
typed shape).

### 3. Trailing-slash strip on `basePath`

You currently pass `CLIENTHUB_URL` to `Configuration` directly:

```typescript
const config = new Configuration({
  basePath: CLIENTHUB_URL,
  apiKey: () => CLIENTHUB_API_KEY,
});
```

The canonical strips trailing slashes defensively:

```typescript
const config = new Configuration({
  basePath: CLIENTHUB_URL.replace(/\/+$/, ""),
  apiKey: () => CLIENTHUB_API_KEY,
});
```

If `CLIENTHUB_URL` is ever set with a trailing slash (common in
.env files), the SDK will produce double-slashed URLs without this
strip.

### 4. Drop the `Promise<any>` lookup cast

In `appendCommunication`, you currently have:

```typescript
const lookupResult = (await lookup.lookupEmailApiV1LookupEmailEmailGet(
  { email: input.email },
  { signal },
)) as { matches?: Array<{ uuid: string }>; count?: number };
```

Replace with the typed form:

```typescript
const lookupResult = await lookup.lookupEmailApiV1LookupEmailEmailGet(
  { email: input.email },
  { signal },
);
// lookupResult is now Promise<LookupResponse> with proper types
```

`lookupResult.matches[0].uuid` is now a typed string, no cast.

## Easiest path: paste-replace `lib/client-hub.ts`

The canonical reference module is 305 lines and exposes the
**identical public surface** you have today
(`logConversion`, `logConversionBackground`, `appendCommunication`,
`appendCommunicationBackground`, `splitName`, `readRequestMeta`,
`ConversionEvent`, `LogConversionInput`, `AppendCommunicationInput`).
Call sites at `app/api/contact/route.ts` and `lib/scheduler-init.ts`
do **not** need to change.

Pull the canonical as the source of truth:

```bash
# Inside the CO consumer site repo
curl -sf https://raw.githubusercontent.com/stancel/client-hub/master/docs/Cross-Project-Integration.rst \
  | awk '/^.. code-block:: typescript$/{flag=1; next} /^.. _client-hub-cp-usage:/{flag=0} flag' \
  > /tmp/canonical-client-hub.ts.fragment
# Inspect /tmp/canonical-client-hub.ts.fragment, then drop into lib/client-hub.ts
```

(Or just open the raw file in a browser, copy the TypeScript code
block, paste it over your existing `lib/client-hub.ts`. Manual
paste is fine — the diff is small enough to review by eye.)

## Install / upgrade

```bash
cd /home/brad/Sites/clever-orchid-website
# In package.json change "@bradstancel/clienthub-sdk": "^0.3.5" -> "^0.3.6"
npm install @bradstancel/clienthub-sdk@^0.3.6
```

Your existing `.npmrc` already authorizes the install — no auth
setup needed.

## Local pre-flight checks

Per your project's CLAUDE.md / README:

```bash
npm run typecheck   # tsc --noEmit
npm run lint
npm run build
```

The lookup-cast removal in step 4 above will **fail typecheck** if
you skip it — that's the point: the typed `LookupResponse` from
v0.3.6 surfaces the cast as redundant. Fix the call site to drop
the `as { ... }` and let TypeScript infer.

## Commit + deploy flow

```bash
# In the consumer-site repo
git add package.json package-lock.json lib/client-hub.ts
git commit -m "chore: adopt @bradstancel/clienthub-sdk@^0.3.6 + canonical lib/client-hub.ts"
git push
# On the production VPS, follow the standard deploy procedure
# from your project's CLAUDE.md (typically scripts/deploy.sh).
```

Verify post-deploy:

```bash
# On the production VPS
node -e "console.log(require('@bradstancel/clienthub-sdk/package.json').version)"
# expected: 0.3.6
```

## Reference

Inside the Client Hub project (`~/docker/client-hub`):

- `CHANGELOG.rst` `v0.3.6` entry — full release notes
- `docs/Cross-Project-Integration.rst` — canonical reference
  module (the source of `lib/client-hub.ts`)
- `api/app/schemas/lookup.py` — the new `LookupResponse` model
- `scripts/deploy-all-vpses.sh` — multi-VPS deploy orchestrator
  (used to deploy the API side; you don't need this on the
  consumer side)

## Questions or anything unclear

- API URL: `https://client-hub-clever-orchid.onlinesalessystems.com`
- OpenAPI spec: same URL + `/openapi.json` (now reports
  `info.version: 0.3.6`)
- For SDK install issues, see `~/docker/verdaccio/CLAUDE.md` on
  Cybertron (registry config + scope policy).
