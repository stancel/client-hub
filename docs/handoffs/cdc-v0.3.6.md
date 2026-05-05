# Client Hub v0.3.6 — Knowledge Transfer for Complete Dental Care Website

**Audience:** the Claude Code session (or developer) working on the
**Complete Dental Care Next.js consumer site** (the one at
`/home/brad/Sites/complete-dental-care-nextjs`, repo
`stancel/complete-dental-care-columbia-website-nextjs`, master
branch).

**Status:** Client Hub v0.3.6 is **already deployed** (commit
`4176b92`, both API VPSes healthy at `0.3.6`) and
`@bradstancel/clienthub-sdk@0.3.6` is **published** to
`https://npm.onlinesalessystems.com/`. CDC's existing v0.3.5 SDK
integration **keeps working unchanged** — v0.3.6 only tightens
types and adds quality gaps that align you with the new canonical
reference module. Adopting v0.3.6 is recommended, not urgent.

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
- Test, commit, deploy on the standard CDC VPS deploy procedure.

## What you specifically need to adopt from the canonical

CDC's v0.3.5 `lib/client-hub.ts` (commit `0b46c9e`) is structurally
sound and was used as one of the two inputs that produced the
canonical. The three things you need to pull in are CO's
contributions to the synthesis:

### 1. Lazy `apiKey` Configuration

You currently have:

```typescript
function buildConfig(): Configuration {
  return new Configuration({
    basePath: CLIENTHUB_URL.replace(/\/+$/, ""),
    apiKey: CLIENTHUB_API_KEY,
  });
}
```

Replace with the lazy-function form so the env var is re-read on
each call (matters for HMR / dynamic env reload):

```typescript
const config = new Configuration({
  basePath: CLIENTHUB_URL.replace(/\/+$/, ""),
  apiKey: () => CLIENTHUB_API_KEY,
});
```

### 2. Cached `getClients()` to stop reallocating per call

You currently rebuild config + clients **on every `logConversion`
call**:

```typescript
try {
  const config = buildConfig();
  const contactsApi = new ContactsApi(config);
  const communicationsApi = new CommunicationsApi(config);
  // ...
}
```

Replace with the cached-clients pattern from the canonical:

```typescript
let cachedClients: {
  contacts: ContactsApi;
  communications: CommunicationsApi;
  lookup: LookupApi;
} | null = null;

function getClients() {
  if (cachedClients) return cachedClients;
  const config = new Configuration({
    basePath: CLIENTHUB_URL.replace(/\/+$/, ""),
    apiKey: () => CLIENTHUB_API_KEY,
  });
  cachedClients = {
    contacts: new ContactsApi(config),
    communications: new CommunicationsApi(config),
    lookup: new LookupApi(config),
  };
  return cachedClients;
}
```

Then call sites switch from `const { contacts, communications } =
{ contacts: new ContactsApi(buildConfig()), ... }` to
`const { contacts, communications } = getClients();`.

### 3. Drop the `Promise<any>` lookup cast

In `appendCommunication`, you currently have:

```typescript
const lookup = (await lookupApi.lookupEmailApiV1LookupEmailEmailGet(
  { email: input.email },
  { signal: controller.signal },
)) as { matches?: Array<{ uuid: string }>; count?: number };
```

Replace with the typed form:

```typescript
const lookup = await lookupApi.lookupEmailApiV1LookupEmailEmailGet(
  { email: input.email },
  { signal: controller.signal },
);
// lookup is now Promise<LookupResponse> with proper types
```

`lookup.matches[0].uuid` is now a typed string, no cast.

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
# Inside the CDC consumer site repo
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
cd /home/brad/Sites/complete-dental-care-nextjs
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

The lookup-cast removal in step 3 above will **fail typecheck** if
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

- API URL: `https://client-hub-complete-dental-care.onlinesalessystems.com`
- OpenAPI spec: same URL + `/openapi.json` (now reports
  `info.version: 0.3.6`)
- For SDK install issues, see `~/docker/verdaccio/CLAUDE.md` on
  Cybertron (registry config + scope policy).
