.. _client-hub-spam-defense-pattern:

######################################################################
Client Hub — Spam Defense Pattern
######################################################################

.. _client-hub-sdp-overview:

**********************************************************************
Overview
**********************************************************************

Defense-in-depth spam filtering at the Client Hub API ingestion
layer. Every public-ish entry point (web form submissions, webhook
ingestion from external SaaS, future integrations) inherits the
same filtering framework with one line of glue code per integration.

This is **defense in depth, not the primary defense.** Consumer
websites already run their own browser-side and form-side filters
(honeypot, time-to-submit, Cloudflare Turnstile, server-side
blocklists). The Client Hub filter exists to:

1. Catch what the consumer-side filter misses (drift between sites,
   different rule sets, different deploy cadence).
2. Protect endpoints that bypass the consumer site (direct API
   calls with a leaked key, webhook callbacks from external SaaS).
3. Serve as the canonical source of truth for spam patterns —
   consumer sites pull patterns from Client Hub at build time so
   "one update fans out to every site."
4. Provide centralized observability — which endpoints get attacked
   most, which patterns produce the most hits, which patterns are
   producing false positives.

.. _client-hub-sdp-mode:

**********************************************************************
Mode — Hard Reject + Spam Events Log
**********************************************************************

Spam payloads are rejected with HTTP 422 before any DB write to
``contacts`` / ``communications`` / etc. The rejection is logged to a
dedicated ``spam_events`` table, never to the primary entity tables.

Rationale (operational/observability data lives in DB tables, never
files — see ``MEMORY.md``):

- Primary tables (``contacts``, ``communications``, ``orders``,
  ``invoices``) stay clean. No ``is_spam`` columns to filter
  against in every read query. No FK pollution risk where a
  spammer-injected booking creates ghost orders.
- Attack history is preserved with full structured detail for
  pattern analysis: which endpoint, which integration kind, which
  source, which pattern matched, the redacted payload itself,
  and a timestamp.
- A future ETL to an OLAP warehouse is a single-table extraction.
- False-positive correction is a single-row UPDATE plus a counter
  bump; no need to "rescue" rows out of the primary tables.

.. _client-hub-sdp-architecture:

**********************************************************************
Architecture
**********************************************************************

Three pillars: a **pattern library** (DB-driven, operator-managed),
an **intake-filter service** (called by every protected endpoint),
and a **rejection log** (the ``spam_events`` table).

.. _client-hub-sdp-tables:

DB tables
======================================================================

``spam_patterns`` — operator-managed pattern library.

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Column
     - Type
     - Notes
   * - id
     - BIGINT UNSIGNED PK
     -
   * - uuid
     - CHAR(36) UNIQUE
     - For external/API use
   * - pattern_kind
     - ENUM
     - One of ``email_substring``, ``url_regex``, ``phrase_regex``,
       ``phone_country_block``, ``full_email_block``
   * - pattern
     - VARCHAR(500)
     - The literal substring or regex (kind-specific)
   * - notes
     - VARCHAR(500) NULL
     - Free-text — what spammer / which incident this came from
   * - is_active
     - BOOLEAN, default TRUE
     - Soft-disable without deleting
   * - hit_count
     - INT UNSIGNED, default 0
     - Bumped on every match; analytics input
   * - last_hit_at
     - DATETIME NULL
     - Most recent match
   * - false_positive_count
     - INT UNSIGNED, default 0
     - Bumped when an operator marks a spam_event as a false
       positive that this pattern caused
   * - created_at / updated_at / created_by
     - standard
     -

``spam_events`` — every rejection logged.

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Column
     - Type
     - Notes
   * - id
     - BIGINT UNSIGNED PK
     -
   * - uuid
     - CHAR(36) UNIQUE
     -
   * - source_id
     - BIGINT UNSIGNED NULL
     - FK → sources.id ON DELETE SET NULL. Which API key submitted.
   * - endpoint
     - VARCHAR(100)
     - e.g. ``/api/v1/contacts``,
       ``/api/v1/webhooks/chatwoot``
   * - integration_kind
     - ENUM
     - ``web_form``, ``webhook``, ``mcp``, ``direct_api``,
       ``other`` — high-level rollup category
   * - remote_ip
     - VARCHAR(45) NULL
     - IPv4 or IPv6 of the original requester (where available;
       webhooks may not know it)
   * - submitted_email
     - VARCHAR(255) NULL
     -
   * - submitted_phone
     - VARCHAR(20) NULL
     -
   * - submitted_body_hash
     - CHAR(16) NULL
     - sha256(body)[:16] for dedup queries
   * - matched_pattern_id
     - BIGINT UNSIGNED NULL
     - FK → spam_patterns.id ON DELETE SET NULL
   * - matched_pattern_text
     - VARCHAR(500) NULL
     - Denormalized copy of the pattern at the time of match;
       survives if the pattern row is later deleted
   * - rejection_reason
     - VARCHAR(64)
     - One of ``phone_invalid``, ``email_blocked``,
       ``url_blocked``, ``phrase_combo``, ``rate_limit``,
       ``honeypot`` (reserved for future)
   * - payload_json
     - JSON NULL
     - Redacted copy of the submitted payload for analysis
   * - was_false_positive
     - BOOLEAN, default FALSE
     - Set by an operator after review
   * - occurred_at
     - DATETIME, default CURRENT_TIMESTAMP
     -

``spam_rate_log`` — sliding-window rate-limit state.

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Column
     - Type
     - Notes
   * - key_type
     - ENUM
     - ``ip``, ``email``, ``email_body_hash``
   * - key_value
     - VARCHAR(255)
     - The actual key
   * - occurred_at
     - DATETIME
     - When this submission was seen
   * - PK
     -
     - Composite (key_type, key_value, occurred_at)

Old rows are pruned opportunistically (DELETE WHERE
``occurred_at < NOW() - INTERVAL 1 HOUR`` on every check). The
sliding window for "rate limited" is 10 minutes.

.. _client-hub-sdp-pattern-kinds:

Pattern kinds
======================================================================

Five pattern kinds, each with deterministic match semantics:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - pattern_kind
     - Match semantics
   * - ``email_substring``
     - Case-insensitive substring of the email's local-part OR
       domain (e.g. ``webdigital`` matches
       ``ezrawebdigital@gmail.com``).
   * - ``full_email_block``
     - Exact, case-insensitive match against the full email
       address. Used for known-bad single addresses.
   * - ``url_regex``
     - Python regex applied to the message body, case-insensitive.
       Used for booking-link blocks (calendly, cal.com, etc.).
   * - ``phrase_regex``
     - Python regex applied to the message body, case-insensitive.
       Two phrase matches in the same body trigger rejection
       (one alone is too noisy; two together is near-certain spam).
   * - ``phone_country_block``
     - Literal substring matched against the **raw** submitted
       phone string before digit-stripping. ``+`` blocks any
       country-code-prefixed number; ``+1`` would NOT block
       (US country code). The "exactly 10 digits, or 11 digits
       starting with 1" check is applied separately as
       ``phone_invalid`` rejection.

.. _client-hub-sdp-flow:

Request flow
======================================================================

For each protected endpoint:

1. The request is parsed by the existing Pydantic schema (typed).
2. An **integration adapter** (a small function alongside the
   handler) maps the typed body into a normalized
   ``IntakePayload``: email, phone, body, ip, source_id.
3. The handler calls
   ``spam_check_or_raise(db, intake, endpoint, integration_kind)``.
4. The service evaluates rules against active patterns:

   - Phone digit-count check.
   - Phone country-code block patterns.
   - Email substring + full-block patterns.
   - Body URL-regex patterns.
   - Body phrase-regex patterns (require ≥2 matches).
   - Rate-limit check (recent hits on ``email`` + ``email||body_hash``
     keys).

5. On match: ``spam_events`` row inserted, pattern's
   ``hit_count`` and ``last_hit_at`` updated, HTTP 422 raised.
6. On no match: a ``spam_rate_log`` row is recorded (so later
   submissions can detect bursts), and the handler proceeds with
   normal DB writes.

.. _client-hub-sdp-inheritance:

**********************************************************************
Adding a new integration (the inheritance pattern)
**********************************************************************

To wire a new integration into the spam-defense framework — five
lines and one helper function:

.. code-block:: python

   # app/routers/your_new_integration.py

   from app.services.spam_filter_service import (
       IntakePayload, spam_check_or_raise,
   )

   def _extract_intake(body: YourPydanticSchema, request: Request) -> IntakePayload:
       return IntakePayload(
           email=body.email,
           phone=body.phone,
           body=body.message,                  # or body.note, etc.
           remote_ip=(request.client.host if request.client else None),
       )

   @router.post("/your-endpoint")
   async def handler(
       body: YourPydanticSchema,
       request: Request,
       ctx: SourceContext = Depends(require_api_key),
       db: AsyncSession = Depends(get_db),
   ):
       intake = _extract_intake(body, request)
       await spam_check_or_raise(
           db, intake,
           source_id=ctx.source_id,
           endpoint="/api/v1/your-endpoint",
           integration_kind="webhook",  # or web_form, mcp, direct_api
       )
       # ... existing handler logic

That's it. The new endpoint inherits all current and future spam
patterns, rate limiting, and observability automatically.

Future integrations explicitly tracked:

- ``/api/v1/webhooks/zammad`` — support ticket pushes
- ``/api/v1/webhooks/marketing-platform`` — campaign attribution
- ``/api/v1/scheduling/*`` — booking portal callbacks
- ``/api/v1/scraping/*`` — web-scraped enrichment ingestion
- ``/api/v1/leads/*`` — direct lead ingestion from advertising

All inherit identical protection without per-integration rule
maintenance.

.. _client-hub-sdp-endpoints:

**********************************************************************
API surface (added in migration 023)
**********************************************************************

Public-ish read (source-scoped API key required) — used by consumer
sites to sync canonical patterns at build time:

- ``GET /api/v1/spam-patterns`` — active patterns only, structured
  by ``pattern_kind`` for easy consumption by the consumer-side
  Python/TS spam-filter modules.

Admin-only (root API key required):

- ``GET /api/v1/admin/spam-patterns`` — full pattern list with
  metadata (hit counts, false-positive counts, inactive rows).
- ``POST /api/v1/admin/spam-patterns`` — create a new pattern.
- ``PUT /api/v1/admin/spam-patterns/{uuid}`` — update an existing
  pattern (toggle is_active, edit notes/text).
- ``DELETE /api/v1/admin/spam-patterns/{uuid}`` — hard-delete (rare;
  prefer is_active=FALSE).
- ``GET /api/v1/admin/spam-events`` — paginated rejection log,
  filterable by ``endpoint``, ``integration_kind``, ``source_uuid``,
  ``rejection_reason``, ``occurred_at`` range, ``was_false_positive``.
- ``GET /api/v1/admin/spam-events/stats`` — aggregates: hits per
  endpoint, hits per pattern, top attacker IPs, false-positive
  rate per pattern.
- ``POST /api/v1/admin/spam-events/{uuid}/mark-false-positive`` —
  set ``was_false_positive=TRUE`` on the event and bump the
  matched pattern's ``false_positive_count``.

.. _client-hub-sdp-false-positives:

**********************************************************************
False-Positive Management
**********************************************************************

Per pattern, the framework tracks ``hit_count`` (true positives +
false positives) and ``false_positive_count`` (operator-marked).
The false-positive rate is ``false_positive_count / hit_count``.

When an operator notices a legitimate submission was rejected:

1. Find the rejection in
   ``GET /api/v1/admin/spam-events?submitted_email=<email>``.
2. ``POST /api/v1/admin/spam-events/{uuid}/mark-false-positive``.
3. The pattern's ``false_positive_count`` is bumped.
4. If a pattern's false-positive rate exceeds a threshold, the
   stats endpoint flags it for review. Operators can disable the
   pattern (PUT is_active=false) or refine it (PUT pattern=...).

The matched ``spam_events`` row stays put — there's no
"reprocessing" path that retroactively creates the missed contact.
Operators contact the customer directly via whatever channel
makes sense (typically the email address that was rejected).

.. _client-hub-sdp-rate-limit:

**********************************************************************
Rate Limit Semantics
**********************************************************************

Sliding window of 10 minutes. Two key types:

- ``(email, occurred_at)`` — same email submitting twice within
  10 minutes is rate-limited.
- ``(email||body_hash, occurred_at)`` — same email + identical body
  hash within 10 minutes is rate-limited (catches the Sophie Lane
  double-submit pattern).

Rate-limit hits are themselves logged to ``spam_events`` with
``rejection_reason='rate_limit'`` and ``matched_pattern_id=NULL``
(no pattern caused this; it's a behavioral signal).

The ``spam_rate_log`` table is pruned opportunistically — every
write deletes rows older than 1 hour, keeping it bounded.

Multi-worker safety: the table is the source of truth, so
multiple uvicorn workers see consistent state without Redis or
in-process coordination.

.. _client-hub-sdp-consumer-sync:

**********************************************************************
Consumer-Site Pattern Sync
**********************************************************************

Consumer sites (Complete Dental Care, Clever Orchid, future Web
Factory sites) pull canonical patterns from the Client Hub at
build/deploy time. One source of truth — no per-site list
maintenance — and operators update patterns from one place
(Client Hub admin) for instant fan-out on next deploy.

This is the scaffolding both Complete Dental Care
(``~/Sites/complete-dental-care-nextjs/``) and Clever Orchid
(``~/Sites/clever-orchid-nextjs/``) shipped on 2026-04-29 as the
canonical reference implementation. Future Web Factory sites
should follow the same shape.

.. _client-hub-sdp-consumer-files:

Files
======================================================================

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - File
     - State
     - Purpose
   * - ``scripts/fetch-spam-patterns.mjs``
     - new
     - prebuild fetch (fail-closed by default); ``--allow-fallback``
       flag for the rare CI/dev rescue case; auto-loads
       ``.env.local``. Validates the 5-key shape before writing.
   * - ``lib/spam-patterns-fallback.json``
     - new (committed)
     - Sorted snapshot of the canonical list at cutover. Used only
       when ``--allow-fallback`` is passed (intentional escape
       hatch); never used in a production build. Regenerated
       whenever the operator wants a fresh fallback baseline.
   * - ``lib/generated/spam-patterns.json``
     - new (gitignored)
     - Rewritten on every prebuild from the live Client Hub
       response. Imported by the server-side filter module.
   * - ``lib/spam-filter.ts``
     - refactored
     - Canonical filename across all Web Factory sites (Clever
       Orchid was renamed from ``lib/spam-defense.ts`` to match
       on 2026-04-29). Hardcoded array constants removed;
       replaced with imports from
       ``lib/generated/spam-patterns.json``. New
       ``isBlockedPhoneCountry`` helper runs BEFORE the digit-
       count check (otherwise ``+235 6 89 50 54`` strips to 10
       digits and would falsely pass). Email blocklist now also
       checks ``full_email_block`` for exact matches.
   * - ``app/api/contact/route.ts`` and any other ingestion route
     - small wiring change
     - Country-code check called before email-block check.
       Otherwise unchanged.
   * - ``package.json``
     - 2-3 hooks
     - ``"prebuild"`` runs the fail-closed fetch; ``"postinstall"``
       (optional) runs an idempotent ``--seed`` so a fresh clone
       has a usable pattern file before the first build.
       ``"predev"`` is the per-site policy decision (see below).
   * - ``.gitignore``
     - +1 line
     - ``lib/generated/`` so the build artifact never gets
       committed.

.. _client-hub-sdp-fetcher:

The fetcher script
======================================================================

``scripts/fetch-spam-patterns.mjs`` does five things:

1. Read ``CLIENTHUB_URL`` and ``CLIENTHUB_API_KEY`` (or
   ``CLIENTHUB_SOURCE_KEY``) from the process environment.
   Auto-load ``.env.local`` for local dev.
2. Issue ``GET <CLIENTHUB_URL>/api/v1/spam-patterns`` with the
   ``X-API-Key`` header.
3. Validate the response: must be a JSON object with exactly five
   keys (``email_substring``, ``full_email_block``, ``url_regex``,
   ``phrase_regex``, ``phone_country_block``), each an array of
   strings.
4. Sort each array (so generated builds are byte-for-byte
   reproducible) and write to ``lib/generated/spam-patterns.json``
   with stable indentation.
5. Exit ``1`` on any failure unless ``--allow-fallback`` is passed,
   in which case copy ``lib/spam-patterns-fallback.json`` into
   ``lib/generated/spam-patterns.json`` and continue with a loud
   warning. The ``--seed`` variant runs the same logic but is a
   no-op if the generated file already exists (used in
   ``postinstall`` hooks).

.. _client-hub-sdp-fail-closed:

Fail-closed by default
======================================================================

Production builds fail-closed — if Client Hub is unreachable, the
build fails and the previous successful build's deployed bundle
keeps serving. The site never silently deploys with stale or empty
patterns. Concretely:

- ``"prebuild"`` runs the fetcher with NO ``--allow-fallback``
  flag. Any fetch failure aborts the build.
- ``"postinstall"`` runs ``fetch-spam-patterns.mjs --seed``. This
  is idempotent — if ``lib/generated/spam-patterns.json`` already
  exists (from a prior install) it does nothing. Used only to
  give fresh clones a usable pattern file before their first
  build attempt.

.. _client-hub-sdp-predev-policy:

``predev`` policy is per-site
======================================================================

Two valid choices — pick what fits each environment:

**Permissive** (Clever Orchid choice): ``"predev"`` runs the
fetcher with ``--allow-fallback``. Local ``npm run dev`` works in
the absence of Client Hub credentials, useful for Docker Compose
dev or first-time setup. Trade-off: a developer's local env won't
surface a Client Hub outage.

**Strict** (default if unsure): no ``"predev"`` hook, OR the same
fail-closed fetch as ``"prebuild"``. Local dev requires the
Client Hub creds in ``.env.local``. Trade-off: slightly more
friction on first-time setup, but ``npm run dev`` and
``npm run build`` behave identically.

.. _client-hub-sdp-cross-site-invariant:

Cross-site invariant
======================================================================

The diff between any two Web Factory sites' fetcher / filter /
fallback files is **only env-var values** (a different
``CLIENTHUB_URL`` and ``CLIENTHUB_API_KEY`` per site). The script,
the file paths, the type interface, the fallback structure, and
the runtime logic are all byte-equivalent across sites. This is a
deliberate property — spam-defense logic is canonical across all
Client Hub deployments, which is the entire point of moving the
patterns into Client Hub in the first place.

Verified across both deployed sites (Complete Dental Care and
Clever Orchid) on 2026-04-29 after Clever Orchid renamed its
filter module to match the canonical name. The only allowed
per-site variation is the ``predev`` policy (see "predev policy
is per-site" above) — and even that is a deliberate operator
choice, not accidental drift.

When onboarding a new site:

1. Copy ``scripts/fetch-spam-patterns.mjs``,
   ``lib/spam-patterns-fallback.json``, and the
   ``"prebuild"`` / ``"postinstall"`` hooks verbatim from an
   existing site.
2. Add the site's source-scoped ``CLIENTHUB_API_KEY`` and
   ``CLIENTHUB_URL`` to its env (Vercel project / VPS ``.env``).
3. Refactor the local filter module to import from
   ``lib/generated/spam-patterns.json`` (replace the existing
   hardcoded constants).
4. Run ``npm run build`` once locally to confirm the prebuild
   fetch succeeds and the deployed bundle catches the standard
   payloads (``+235`` country code, ``calendly.com`` URL,
   ``webdigital`` email substring, two-phrase combo).

.. _client-hub-sdp-observability:

**********************************************************************
Observability + Future ETL
**********************************************************************

Designed for ETL to OLAP later (per the
``feedback_observability_in_db.md`` rule).

- Every column on ``spam_events`` is a structured field, not JSON
  blob. Queryable via standard GROUP BY without JSON path tools.
- ``payload_json`` exists for full-fidelity attack analysis but
  the queryable signal columns (email, phone, body_hash, IP,
  pattern, reason, endpoint, integration_kind) live in their own
  columns.
- Foreign keys to ``sources`` and ``spam_patterns`` give referential
  integrity for OLTP queries; the denormalized
  ``matched_pattern_text`` column survives pattern deletion so
  historical analysis isn't lost.
- All timestamps in UTC.

When the OLTP store gets too heavy, ETL the ``spam_events`` table
into a warehouse (Snowflake / BigQuery / DuckDB) and DELETE rows
older than N months from the OLTP. The schema is friendly to
this — no derived state, no aggregation tables, no upserts.

.. _client-hub-sdp-references:

**********************************************************************
References
**********************************************************************

- ``migrations/023_spam_patterns_and_events.sql`` — schema
- ``app/services/spam_filter_service.py`` — service module
- ``app/models/spam.py`` — ORM models
- ``app/schemas/spam.py`` — Pydantic schemas
- ``app/routers/spam.py`` — admin + public routers
- ``MEMORY.md → feedback_observability_in_db.md`` — design rule
  this pattern instantiates
- ``MEMORY.md → feedback_3nf_required.md`` — schema is 3NF; no
  denormalized cached pointers, only the deliberate
  ``matched_pattern_text`` for history-survival
