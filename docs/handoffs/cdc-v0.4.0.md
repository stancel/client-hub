# Client Hub v0.4.0 — Knowledge Transfer for Complete Dental Care Website

**Audience:** the Claude Code session (or developer) working on the
**Complete Dental Care Next.js consumer site** at
`/home/brad/Sites/complete-dental-care-nextjs` (repo
`stancel/complete-dental-care-columbia-website-nextjs`, master
branch).

**Status:** Client Hub v0.4.0 is being released alongside this
prompt (driven by the 2026-05-06 SEO-pitch breakthrough at CDC, see
the v0.4.0 entry in `CHANGELOG.rst`). The new SDK `@bradstancel/clienthub-sdk@0.4.0`
will be on the private registry at
`https://npm.onlinesalessystems.com/` after the tag-triggered
publish workflow runs. **The existing v0.3.6 integration keeps
working unchanged** — adopting v0.4.0 closes two real defects on
the consumer-site side that aren't covered by the Client Hub fix
alone.

## TL;DR

1. Bump `@bradstancel/clienthub-sdk` to `^0.4.0` in `package.json`.
2. In `lib/client-hub.ts::logConversion` (around the existing
   `createCommunicationApiV1CommunicationsPost` call, lines ~170–182),
   add `externalRefsJson: externalRefs` to the `commCreate` payload
   — the same `externalRefs` object the contact create already
   receives. Today the comm call sends nothing for it, so the visitor
   IP only lands on the contact, not the comm; v0.4.0 of the API
   accepts it on both.
3. In `lib/client-hub.ts::appendCommunication` (around the
   `createCommunicationApiV1CommunicationsPost` call), add a fresh
   `externalRefsJson` built from the CF-Connecting-IP and User-Agent
   headers of the incoming Next.js request. Add `ipAddress` and
   `userAgent` parameters to `AppendCommunicationInput` so the
   page-level call site can pass them through.
4. In `lib/spam-filter.ts`, add a NANP area-code validator and call
   it in form-submit pre-validation, alongside the existing
   `isValidUSPhone`. This catches the `+12356895054`-style submission
   at the website edge instead of relying on Client Hub.
5. Re-run the prebuild hook (or `npm run prebuild`) to pull the new
   SEO-outreach patterns from `GET /api/v1/spam-patterns` into
   `lib/generated/spam-patterns.json`.
6. Test, commit, deploy.

## Why these changes

**(2) and (3) — comm `externalRefsJson`.** The 2026-05-06
investigation found that the spam_event for the breakthrough comm
recorded the CDC droplet IP (`134.199.195.114`) instead of the
visitor IP (`106.219.155.100`, India). Root cause: your
`logConversion` and `appendCommunication` send `externalRefsJson`
only on the contact create, not the comm. Client Hub v0.4.0 falls
back to the parent contact's stored `external_refs_json.ip_address`
when the comm payload doesn't carry one, so the production data is
already going to be correct after the API deploy. But sending it
explicitly on the comm is the right contract long-term — it means
the comm's `spam_events.remote_ip` reflects the *exact* visitor IP
of that submission (which can differ from the contact-create IP if
the user navigates between forms).

**(4) — NANP area-code validator.** The Davis Brown phone
`+12356895054` slipped past the existing `isValidUSPhone` check (10
digits, leading `1` stripped — passes the count) and the
`phoneCountryIsBlocked` check (the `+1` prefix masks it as
domestic). Area code `235` is not assigned in NANP. Mirror the
list from Client Hub's
`api/app/services/phone_utils.py::NANP_AREA_CODES` (frozenset of
~400 3-digit strings) and add an `isValidNanpAreaCode(area)` helper
+ wire it into the form's `isValidUSPhone` path. Reject early with
the same UX as a normal phone-format error.

**(5) — pattern sync.** Migration 031 on the API seeded 5 new
email substrings (`seowebexpert`, `webexpert`, `webexpertsolution`,
`seoanalyst`, `seospecialist`) and 7 new whitespace-tolerant phrase
regexes covering the SEO-outreach body shape. Your `prebuild` hook
(`scripts/fetch-spam-patterns.mjs`) pulls these automatically — just
make sure a build runs before your next deploy.

## Specifics — changes in `lib/client-hub.ts`

### `logConversion` — add `externalRefsJson` to the comm call

Today (around line 170 in the v0.3.6 module):

```typescript
await communications.createCommunicationApiV1CommunicationsPost(
  {
    commCreate: {
      contactUuid: contact.uuid,
      channel: input.event,
      direction: "inbound",
      occurredAt,
      subject: input.subject ?? "",
      body: input.body ?? "",
    },
  },
  { signal },
);
```

After v0.4.0:

```typescript
await communications.createCommunicationApiV1CommunicationsPost(
  {
    commCreate: {
      contactUuid: contact.uuid,
      channel: input.event,
      direction: "inbound",
      occurredAt,
      subject: input.subject ?? "",
      body: input.body ?? "",
      externalRefsJson: externalRefs,
    },
  },
  { signal },
);
```

(Same `externalRefs` object the contact create already receives —
no new variable needed.)

### `appendCommunication` — accept and forward visitor IP/UA

Add to `AppendCommunicationInput`:

```typescript
export interface AppendCommunicationInput {
  email: string;
  event: ConversionEvent;
  subject?: string;
  body?: string;
  occurredAt?: string;
  ipAddress?: string;        // new
  userAgent?: string;        // new
}
```

Inside the function, build a minimal externalRefs and pass it:

```typescript
const externalRefs: Record<string, unknown> = {
  ip_address: input.ipAddress,
  user_agent: input.userAgent,
  site_source_code: CLIENTHUB_SOURCE_CODE,
};

await communications.createCommunicationApiV1CommunicationsPost(
  {
    commCreate: {
      contactUuid,
      channel: input.event,
      direction: "inbound",
      occurredAt,
      subject: input.subject ?? "",
      body: input.body ?? "",
      externalRefsJson: externalRefs,
    },
  },
  { signal },
);
```

Page-level callers (cancellation hooks, follow-up loggers) need to
extract `CF-Connecting-IP` from the incoming request headers and
pass it through:

```typescript
const ipAddress =
  request.headers.get("cf-connecting-ip") ??
  request.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
const userAgent = request.headers.get("user-agent") ?? undefined;

await appendCommunication({
  email,
  event: "cancellation",
  subject,
  body,
  ipAddress,
  userAgent,
});
```

## Specifics — changes in `lib/spam-filter.ts`

Add `isValidNanpAreaCode`. Mirror the frozenset list from
`api/app/services/phone_utils.py::NANP_AREA_CODES`:

```typescript
const NANP_AREA_CODES = new Set<string>([
  // ... copy from api/app/services/phone_utils.py
]);

export function isValidNanpAreaCode(area: string): boolean {
  return /^[0-9]{3}$/.test(area) && NANP_AREA_CODES.has(area);
}

export function extractNanpAreaCode(phone: string): string | null {
  const digits = phone.replace(/\D/g, "");
  if (digits.length === 11 && digits.startsWith("1")) return digits.slice(1, 4);
  if (digits.length === 10) return digits.slice(0, 3);
  return null;
}
```

Wire into the form-submit validator alongside the existing
`isValidUSPhone`:

```typescript
if (!isValidUSPhone(phone)) {
  // existing rejection
}
const area = extractNanpAreaCode(phone);
if (area && !isValidNanpAreaCode(area)) {
  return { ok: false, reason: "phone_invalid_areacode" };
}
```

Same UX as the existing format error — the user sees "Invalid phone
number" without learning which rule fired.

## Verification

After deploy:

1. Try submitting a contact with phone `+12356895054` — should be
   rejected at the website level with the standard phone-format
   error (no Client Hub round-trip).
2. Submit a clean contact and confirm the resulting Client Hub
   `spam_events` row (via the admin endpoint) has both
   `remote_ip` (canonical visitor IP) and `peer_ip` (CDC droplet)
   populated, and `submitted_email` is non-NULL on any
   `/communications` event.
3. Check that the v0.4.0 SDK didn't regress any existing flows —
   the contact create / lookup-by-email paths are unchanged.

## Cross-reference

- Client Hub `CHANGELOG.rst` v0.4.0 entry — full defect-by-defect
  walkthrough.
- `docs/Spam-Defense-Pattern.rst` — updated subsections "Visitor IP
  vs proxy peer" and "Phone validation: digit count vs NANP area
  code".
- `docs/Cross-Project-Integration.rst` — the canonical
  `lib/client-hub.ts` reference module will be updated after both
  consumer sites adopt v0.4.0.

Adoption is on your schedule. The Client Hub-side fixes are
fix-forward and don't require this consumer-site work to land —
but the long-term contract is "every API call carries
`externalRefsJson` with `ip_address`", so the sooner the better.
