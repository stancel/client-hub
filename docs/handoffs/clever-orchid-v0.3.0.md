# Client Hub v0.3.0 — Knowledge Transfer for Clever Orchid Website

**Audience:** the Claude Code session (or developer) working on the
**Clever Orchid Next.js consumer site** (the one that submits
contact-form and booking-form data to
`https://client-hub-clever-orchid.onlinesalessystems.com`).

**Status:** Client Hub v0.3.0 is **already deployed** to the Clever
Orchid VPS. Nothing on the consumer site has to change today for
things to keep working. This document explains **what changed**,
**what you're already doing right**, and **what to plan for** when
paid traffic (ads, email outreach) starts later this year.

## What changed in Client Hub v0.3.0

### 1. Phone numbers are normalized server-side to E.164

Previously the API stored phone numbers verbatim — whatever the form
submitted. That broke the planned SIP/CTI caller-lookup integration
because the lookup endpoint does literal string equality and the same
human's number could be stored as `(803) 555-1212` or `8035551212` or
`+18035551212` depending on which form they used.

**v0.3.0 contract:** the API normalizes every inbound phone to E.164
(`+15551234567`) before storage. The Pydantic validator on
`POST /api/v1/contacts` accepts any of these inputs and converts them
in flight:

```
8035551212        → +18035551212
803-555-1212      → +18035551212
(803) 555-1212    → +18035551212
803.555.1212      → +18035551212
1-803-555-1212    → +18035551212
+18035551212      → +18035551212
```

**What this means for the Clever Orchid site:** **nothing**. Keep
submitting phone numbers in whatever format the form collects them.
The API handles the normalization. If you want to *display* a
normalized phone elsewhere, you can match the API's behavior using
any standard E.164 library, but it's not required.

The existing phone data on the Clever Orchid VPS was backfilled to
E.164 in the v0.3.0 migration (027). All 17 contacts on Clever
Orchid now have E.164 phones — including the one entry stored as
`(808) 256-8182` that was a SIP-lookup landmine.

### 2. Marketing-source attribution is now populated

Previously the `contact_marketing_sources` junction was completely
empty (zero rows on Clever Orchid, despite 17 contacts). The API
contract has supported a `marketing_sources: list[str]` field on
`POST /api/v1/contacts` since v0.1.0 — but the consumer site never
sent it, so the table sat unused.

**v0.3.0 contract:** the API now derives marketing-source codes
server-side when the consumer site doesn't supply them. Derivation
logic (in priority order):

1. UTM params in `external_refs_json.extra.utm_*` → `google_search` /
   `social_media_ad` / `social_media_organic` / `other` (email)
2. Referrer hostname → `google_search` (google.com / bing.com / etc.)
   / `social_media_organic` (facebook.com / x.com / etc.) / `website`
   (anything else, including same-domain navigation — the SEO case)
3. No signal at all → `website` (conservative default)

**Backfill:** the existing 17 contacts on Clever Orchid have been
retroactively attributed via
`scripts/backfill-marketing-sources.sql`. They all mapped to
`Website` because the captured referrer was always the consumer
site's own domain (the user navigated within the site before
submitting, so `document.referrer` at submit time was a same-domain
URL — the SEO landing referrer was lost). That's the honest answer
given the data we have.

**What this means for the Clever Orchid site today:** **nothing**.
Current traffic is 100% SEO/inbound and we're not capturing
first-touch UTMs or the original landing referrer, so the API will
continue to attribute these contacts as `website`. That's correct.

### 3. New public endpoint: `GET /api/v1/marketing-sources`

Source-key gated, mirrors the existing `/spam-patterns` pattern.
Returns the canonical marketing-source code list:

```json
{
  "data": [
    {"code": "google_search",        "label": "Google Search"},
    {"code": "social_media_ad",      "label": "Social Media Ad"},
    {"code": "social_media_organic", "label": "Social Media (Organic)"},
    {"code": "referral",             "label": "Referral"},
    {"code": "walk_in",              "label": "Walk-In"},
    {"code": "phone_call",           "label": "Phone Call"},
    {"code": "website",              "label": "Website"},
    {"code": "word_of_mouth",        "label": "Word of Mouth"},
    {"code": "repeat",               "label": "Repeat Customer"},
    {"code": "other",                "label": "Other"}
  ]
}
```

**When you'll need it:** when Clever Orchid starts running paid ads
or email outreach (see "Future work" below). At that point the
consumer site will explicitly set `marketing_sources: ["google_search"]`
(etc.) on the POST and you can pull this list at build time to
validate / populate any UI dropdowns rather than hardcoding the codes.

## What the Clever Orchid site is already doing correctly

Verified against the actual production payloads landing in
`contacts.external_refs_json`:

- ✅ `ip_address` — the real visitor IP from `CF-Connecting-IP` is
  forwarded server-side. v0.2.0 made this the canonical IP source for
  spam_rate_log and spam_events.
- ✅ `user_agent` — captured.
- ✅ `referrer` — `document.referrer` from the form-submit page.
- ✅ `source_page` — current pathname.
- ✅ `extra.form_name` / `extra.service_name` / `extra.appointment_id` /
  `extra.staff_name` / `extra.start_date` — booking-flow context with
  rich detail.
- ✅ Honeypot field, time-to-submit check, Cloudflare Turnstile — all
  three are operating; no changes needed.

**Don't change any of the above.** v0.3.0 builds on top of these.

## Future work (no action needed today; for when paid traffic starts)

When Clever Orchid launches paid ads, email outreach, or any
non-organic campaign — likely later this year, possibly tied to
seasonal embroidery / monogramming campaigns — the consumer site
should add **first-touch UTM capture**:

1. **On every page load**, check `URLSearchParams` for `utm_source`,
   `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`. If any
   are present, persist to a first-touch cookie (`first_touch_utm`,
   30-day expiry). Don't overwrite if the cookie already exists —
   first touch wins.
2. **On form submit**, read the cookie and forward into the POST:

   ```js
   external_refs_json: {
     ip_address: cfConnectingIp,
     user_agent: req.headers['user-agent'],
     referrer: document.referrer,
     source_page: window.location.pathname,
     extra: {
       form_name: 'contact',  // or 'booking'
       // booking-specific fields you already send (service_name,
       // appointment_id, staff_name, start_date) stay as-is
       // NEW — populated from first_touch_utm cookie:
       utm_source:   firstTouchUtm.source,
       utm_medium:   firstTouchUtm.medium,
       utm_campaign: firstTouchUtm.campaign,
       utm_content:  firstTouchUtm.content,
       utm_term:     firstTouchUtm.term,
     },
   }
   ```

3. **Optionally** also set the explicit field if you'd rather decide
   the canonical code on the consumer side rather than letting the
   API derive it:

   ```js
   marketing_sources: ['google_search']  // pulled from /api/v1/marketing-sources
   ```

   Pull the canonical code list at build time the same way the spam
   patterns are pulled (see `lib/marketing-sources.ts` if it exists,
   or model after `lib/spam-filter.ts`).

The API is ready for both signals today; flip them on whenever the
ad campaigns go live.

## Verification

You can confirm v0.3.0 is live and behaving by hitting:

```bash
curl -sf https://client-hub-clever-orchid.onlinesalessystems.com/openapi.json \
  | jq -r '.info.version'
# expected: 0.3.0
```

And check that submitted phones are stored E.164 by spot-checking the
admin events endpoint with the root API key.

## What to do with this document

- Read it once, mentally diff against your current contact-form /
  booking-form code path, confirm nothing needs to change today.
- File it under the consumer-site repo's `docs/` so the next session
  has it.
- Reference it when Clever Orchid's paid-traffic campaigns spin up —
  the "Future work" section is the implementation checklist.

## Questions or anything unclear

The Client Hub project itself is the source of truth. The relevant
files in `~/docker/client-hub`:

- `api/app/services/phone_utils.py` — phone normalizer
- `api/app/services/marketing_source_service.py` — derivation rules
- `api/app/routers/marketing_sources.py` — the public endpoint
- `api/app/schemas/contact.py::ContactCreatePhone` — the Pydantic
  validator that does the normalization at ingestion
- `migrations/027_phone_e164_normalization.sql` — the backfill +
  CHECK constraint
- `scripts/backfill-marketing-sources.sql` — the one-shot junction
  backfill
- `docs/Spam-Defense-Pattern.rst` — the broader contract for the
  consumer-side / API-side filter sync (the same pattern applies for
  marketing sources via the new endpoint)
