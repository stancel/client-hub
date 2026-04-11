.. _installation-implementation-prompt:

######################################################################
Client Hub — Installation & Multi-Source Implementation Prompt
######################################################################

:Target audience: Claude Code session opened in ``~/docker/client-hub/``
:Created: 2026-04-11
:Created by: Cross-project planning session in
             ``~/Sites/complete-dental-care-nextjs``
:Estimated scope: 1–2 day session of coding + testing


.. contents:: Table of Contents
   :local:
   :depth: 2


**********************************************************************
How to use this document
**********************************************************************

This is a self-contained implementation prompt. Paste it into a fresh
Claude Code session opened in ``~/docker/client-hub/`` (or tell that
session to read this file directly) and it will contain everything
needed to execute the work end-to-end without re-deriving context.

**Your job, if you're the implementation session reading this:**

1. Read this prompt in full before doing anything.
2. Use ``TaskCreate`` to break it into tracked tasks.
3. Execute the deliverables in the order they're listed.
4. Run the full verify workflow (CI-equivalent) before committing.
5. Commit in logical chunks with clear messages.
6. When done, push to master and notify Brad so he can kick off the
   first VPS deployment (the VPS is already provisioned at
   ``client-hub-complete-dental-care.onlinesalessystems.com``).

**What you are NOT doing on this pass:**

- Live InvoiceNinja / Chatwoot / Zammad integrations (future TODO)
- Refactoring the existing 23 API endpoints beyond the
  multi-source auth changes listed in Goal B
- Touching Brad's existing development instance on Cybertron at
  ``10.0.1.220``
- Building a front-end admin UI
- Migrating data from the dental care site's
  ``data/conversions.jsonl`` (that's a Next.js-side task for a
  later session)


**********************************************************************
Context
**********************************************************************

Client Hub is Brad's **Customer & Prospect Intelligence system**.
Every "Web Factory" Next.js site he builds (starting with
``complete-dental-care-nextjs`` and his wife's
``clever-orchid-website``) will funnel conversion events —
contact form submits, appointment bookings, phone-click events,
scroll-depth, etc. — into client-hub. The data gets enriched there
and feeds the downstream ecosystem: ad retargeting, follow-up
sequences, CTI integrations, and reporting via Brad's OpsInsights
SaaS product.

**Critical architectural point — read carefully:**

Client Hub remains **single-tenant per company**. One company =
one client-hub instance = one MariaDB database containing only
that company's data. Complete Dental Care's client-hub instance
lives on its own DigitalOcean droplet with its own DB. Clever
Orchid's client-hub instance is a completely separate deployment
on a different droplet with a different DB. No customer data is
ever mixed across companies.

**Inside a single company's instance**, however, many different
**sources** push events in. For Complete Dental Care that might
include:

- ``dental_care_website`` — the public Next.js site
- ``dental_care_scheduler`` — the booking flow
- ``dental_care_ads_veneers`` — the veneers Google Ads landing page
- ``dental_care_chatwoot`` — inbound chats and texts
- ``dental_care_cti`` — the SIP phone system integration
- ``dental_care_invoiceninja`` — billing sync

Each of these is a **source** inside the single client-hub
instance. Each source has its own API key so the practice can
see which system logged which event, revoke a leaked key without
taking down every other integration, and run reports filtered by
source.

**Source terminology note:** there is already a ``marketing_sources``
lookup table (google_search, social_media_ad, referral, walk_in,
etc.) that tracks *where a lead discovered the business*. The new
``sources`` table is about *which system logged the event*. Different
concepts. Document this distinction clearly in
``docs/Multi-Source.rst``.

Today, client-hub runs as a LAN-only development instance on
Brad's home lab (``10.0.1.220:8800`` on Cybertron), depending on
the shared MariaDB instance at ``~/docker/mariadb/`` via an
external Docker network called ``my-main-net``. This setup works
for local dev but is not reachable from the public Web Factory
sites deployed on DigitalOcean.

**This implementation prompt's purpose:**

1. Package client-hub into a **one-line bash installer**
   (Ollama-style ``curl -fsSL .../install.sh | sudo bash``) that
   provisions a fresh Ubuntu/Debian LTS VPS from zero to a running,
   TLS-secured, backed-up, smoke-tested instance in under 10
   minutes.
2. Refactor the schema and API auth model to support **per-source
   attribution** — every write stamps its originating source via
   the API key used, so queries and reports can break data down by
   source within the single company's database.
3. Ship the standardized **cross-project event vocabulary** so
   every Web Factory site uses the same ``channel_types`` codes
   and ``external_refs_json`` convention — integrating a new site
   becomes a ~30-minute copy-paste job.
4. Document the integration pattern for the first consumer
   (``complete-dental-care-nextjs``) so it's copy-paste portable
   to every future Web Factory site and non-web source system.

**Cross-project context documents** (in the dental care repo — read
these if you have doubts about the why of any decision below):

- ``~/Sites/complete-dental-care-nextjs/docs/Growth-Opportunities.rst``
- ``~/Sites/complete-dental-care-nextjs/docs/Google-Business-Profile-Setup.rst``
- ``~/Sites/complete-dental-care-nextjs/docs/Conversion-Tracking-Plan.rst``
- ``~/Sites/complete-dental-care-nextjs/CLAUDE.md``


**********************************************************************
Current state snapshot — read carefully
**********************************************************************

These are the non-obvious facts about the existing codebase that
shape the implementation. They were verified by direct code
inspection on 2026-04-11. Don't re-derive them; work from here.

Runtime topology
======================================================================

``docker-compose.yml`` currently defines **only** the
``client-hub-api`` service. There is no MariaDB service in this
compose file. It connects to ``mariadb:3306`` on the external
Docker network ``my-main-net``, which is defined in
``~/docker/mariadb/`` and is not part of this repo.

On a fresh VPS where ``~/docker/mariadb/`` does not exist, neither
does the network. The installer must stand up a **bundled** mode
where MariaDB, the API, and Caddy all live in one compose file.

API container
======================================================================

- **Language:** Python 3.12
- **Framework:** FastAPI + SQLAlchemy (async) + aiomysql
- **Port:** 8800 (internal), mapped to 8800 on host
- **Dockerfile:** ``api/Dockerfile`` — simple, no multi-stage
- **Entrypoint:**
  ``uvicorn app.main:app --host 0.0.0.0 --port 8800``
- **Auth:** ``X-API-Key`` header middleware (currently matches a
  single global ``API_KEY`` env var — this must change for
  per-source attribution)
- **Health check:** ``GET /api/v1/health`` (no auth required)
- **OpenAPI spec:** ``GET /openapi.json``
- **Swagger UI:** ``GET /docs``
- **Redoc:** ``GET /redoc``

Env var contract (see ``api/app/config.py``):

.. code-block:: python

   db_host: str = "mariadb"
   db_port: int = 3306
   db_name: str = "dev_schema"
   db_user: str = "clienthub"   # NOTE: compose passes DB_USER=root
                                # today — we will standardize on
                                # "clienthub" everywhere
   db_password: str = ""
   api_key: str = "dev-api-key"
   api_host: str = "0.0.0.0"
   api_port: int = 8800

Migration runner
======================================================================

There is no Alembic or embedded runner. Migrations are plain
numbered SQL files in ``migrations/`` applied in order via a shell
loop. The canonical pattern is from ``.github/workflows/ci.yml``:

.. code-block:: bash

   for f in migrations/0*.sql; do
     mariadb -h 127.0.0.1 -u root -ptest_root_password test_schema < "$f"
   done

Current migration files (1–13):

- ``001_lookup_tables.sql`` — 11 lookup tables (contact_types,
  channel_types, marketing_sources, etc.)
- ``002_business_settings.sql`` — singleton business config
- ``003_organizations.sql`` — organizations table
- ``004_contacts.sql`` — central contacts entity, includes an
  ``external_refs_json`` JSON column (NULL by default)
- ``005_contact_details.sql`` — phones, emails, addresses
- ``006_org_details.sql`` — org phones, emails, addresses
- ``007_contact_prefs_and_junctions.sql`` — tags, marketing sources
- ``008_orders.sql`` — orders + line items + status history
- ``009_invoices_payments.sql`` — invoices, payments
- ``010_communications.sql`` — event/interaction log
- ``011_seed_lookup_data.sql`` — reference data for lookup tables
- ``012_seed_test_data.sql`` — test data (dev/test only)
- ``013_marketing_optouts_and_preferences.sql`` — opt-out flags,
  preferences, ``v_contact_summary`` and ``v_contact_last_order``
  views

**Key schema facts for this implementation:**

- ``contacts.external_refs_json`` is JSON, NULL by default, no
  documented convention. We're going to formalize it.
- ``channel_types`` currently has 6 seeded rows: ``sms``, ``email``,
  ``phone``, ``chat``, ``portal``, ``in_person``. **None of the
  Web Factory event codes exist yet.** We will add them.
- **No ``source_id`` column exists anywhere.** The README and
  CLAUDE.md both say "Single-tenant by design — one database per
  business." That philosophy is not changing — client-hub remains
  one database per company — but we ARE adding a new
  within-database concept of ``sources`` for per-system
  attribution. Different concept, same "single-tenant per company"
  guarantee.

Existing scripts
======================================================================

- ``scripts/generate-sdks.sh`` — Docker-based OpenAPI SDK
  generator. Supports ``python``, ``php``, ``typescript``, or
  ``all``. Takes ``CLIENT_HUB_API_URL`` from env (defaults to
  ``http://10.0.1.220:8800``). Uses
  ``openapitools/openapi-generator-cli:v7.12.0``.

This is the **only** existing script. No install, deploy, backup,
or provisioning scripts yet. Clean slate.

Backup story
======================================================================

``backups/`` directory exists but is empty. ``TODO.rst`` lists
"Automated database backups" as a future item. We will ship this.

CI/CD
======================================================================

GitHub Actions at ``.github/workflows/ci.yml`` runs on every push
to master and on PRs. Jobs: lint (ruff + rstcheck) → test (pytest
against a MariaDB 12 service container with all migrations
applied) → build (Docker image) → SDK gen (master only).
**63 tests passing as of 2026-04-05.** Any schema change or API
change must keep CI green.


**********************************************************************
Goals
**********************************************************************

Goal A — One-line installer
======================================================================

A single ``curl -fsSL https://... | sudo bash`` command provisions
a fresh Ubuntu 22.04/24.04 LTS or Debian 12+ VPS from zero to a
running client-hub instance in under 10 minutes. The installer
must:

- Detect OS and refuse to run on anything else
- Install Docker + docker-compose plugin + required system packages
- Create a dedicated ``clienthub`` system user
- Clone or download the repo (see **Source download modes** below)
- Auto-generate all secrets (DB root password, API keys, etc.)
- Write ``/opt/client-hub/.env`` (mode 0600, owned by ``clienthub``)
- Stand up MariaDB 12, the API, and Caddy via docker-compose
- Run all migrations idempotently
- Set up the firewall (ufw) and a nightly backup cron job
- Optionally generate SDKs in the user's chosen language(s)
- Smoke-test the final installation
- Print a clean summary with credentials and next steps

Goal B — Per-source attribution (Option B from planning)
======================================================================

Within a single company's client-hub instance, add explicit
tracking of which *source system* logged each event:

- New ``sources`` table — one row per integration that pushes
  data in (e.g. ``dental_care_website``, ``dental_care_scheduler``,
  ``dental_care_chatwoot``, ``dental_care_cti``)
- New ``api_keys`` table — per-source API credentials with prefix
  indexing and revocation
- ``contacts.first_seen_source_id`` NOT NULL FK — which source
  first created this contact
- ``communications.source_id`` NOT NULL FK — which source logged
  this specific event
- API middleware resolves the ``X-API-Key`` to a ``source_id`` and
  auto-stamps all new contacts / communications with it
- **Reads are NOT scoped by source** — every source-scoped API
  key can read every contact and communication in the DB. This
  matches the business reality: a CTI lookup must be able to find
  a contact that the website previously created. Source
  attribution is for *reporting and write-time stamping*, not
  read-time isolation.
- A root admin API key (in env var) bypasses source context
  entirely and can manage sources, mint new keys, revoke keys,
  and run cross-source reports
- Views (``v_contact_summary``, ``v_contact_last_order``) are
  updated to include source info
- A new ``v_events_by_source`` view gives quick cross-source
  attribution queries
- All existing tests updated to work with the new schema

Goal C — Cross-project event vocabulary and convention
======================================================================

Standardize the event codes and metadata shape used by every Web
Factory site so integrations are copy-paste:

- Add new ``channel_types`` rows for every Web Factory event
  (see the full list in the Standardized vocabulary section below)
- Formalize the ``external_refs_json`` shape — what keys are
  required, what are optional, how they're used
- Ship a reference TypeScript module (``lib/client-hub.ts``) in
  the Cross-Project Integration doc that every Next.js site can
  copy verbatim


**********************************************************************
Non-goals
**********************************************************************

Explicitly out of scope for this implementation:

- Refactoring the existing 23 API endpoints beyond the per-source
  stamping changes listed in Goal B
- Adding new entity types (no new tables beyond ``sources``,
  ``api_keys``, and the ``_schema_migrations`` tracking table)
- Building InvoiceNinja / Chatwoot / Zammad live integrations
- Front-end admin UI (API-only is fine; admin UI is a later project)
- Data migration from existing Cybertron ``10.0.1.220`` dev
  instance (this ships the *new* deployment pattern; migrating
  dev data is a separate, optional task)
- Touching the dental care site's code (that happens after this
  lands, in a separate Next.js session)
- Heroic rewrites of the migration runner to Alembic / etc. Plain
  SQL + the loop pattern is fine and matches the CI workflow
- Kubernetes, Nomad, or any non-docker-compose orchestrator


**********************************************************************
Multi-source architecture (Option B, corrected)
**********************************************************************

Design summary
======================================================================

- A ``sources`` table lists every system that pushes data into
  this company's client-hub instance. Each source has a slug,
  display name, type, and optional description.
- An ``api_keys`` table issues per-source credentials. A source
  can have multiple active keys (for rotation) and keys can be
  revoked without breaking historical data (the source_id is
  preserved on every past insert).
- Every ``contacts`` row carries a ``first_seen_source_id`` NOT
  NULL foreign key — the source that first created this contact.
- Every ``communications`` row carries a ``source_id`` NOT NULL
  foreign key — the source that logged this specific event.
- **Reads are NOT isolated by source.** Any valid source-scoped
  API key can SELECT any contact or communication in the DB.
  This is critical: the CTI system needs to look up contacts
  created by the website, and vice versa.
- **Writes ARE stamped by source.** The API middleware identifies
  the calling source from the ``X-API-Key`` header and
  automatically sets ``source_id`` on every INSERT into
  ``communications`` and ``first_seen_source_id`` on every INSERT
  into ``contacts``. Writes cannot spoof a different source.
- A single reserved **root** API key (held in env var —
  ``CLIENTHUB_ROOT_API_KEY``) bypasses source context entirely and
  can administer sources, mint new keys, revoke keys, and run
  cross-source queries. This key is what the installer prints at
  the end and is used to bootstrap the first source.

Schema changes — new migrations
======================================================================

``migrations/014_sources_and_api_keys.sql``

.. code-block:: sql

   CREATE TABLE sources (
       id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
       uuid CHAR(36) NOT NULL,
       code VARCHAR(64) NOT NULL UNIQUE,           -- slug, e.g. dental_care_website
       name VARCHAR(255) NOT NULL,                 -- display name
       source_type VARCHAR(32) NOT NULL DEFAULT 'website',  -- website|cti|chat|crm|ads|scheduler|other
       domain VARCHAR(255) NULL,                   -- primary public domain if applicable
       description TEXT NULL,
       is_active BOOLEAN NOT NULL DEFAULT TRUE,
       created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       UNIQUE KEY idx_sources_uuid (uuid),
       KEY idx_sources_active (is_active),
       KEY idx_sources_type (source_type)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

   -- IMPORTANT: this table is distinct from marketing_sources.
   --   sources           = system/integration that logged the event
   --                       (website, cti, chatwoot, etc.)
   --   marketing_sources = where the lead originally discovered
   --                       the business (google_search, referral,
   --                       walk_in, etc.)
   -- Do not conflate them.

   CREATE TABLE api_keys (
       id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
       uuid CHAR(36) NOT NULL,
       source_id BIGINT UNSIGNED NOT NULL,
       key_prefix VARCHAR(16) NOT NULL,            -- first 8 chars for admin display
       key_value VARCHAR(128) NOT NULL,            -- full key; see Security below
       name VARCHAR(255) NOT NULL,                 -- label, e.g. "Production write key"
       is_active BOOLEAN NOT NULL DEFAULT TRUE,
       created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       last_used_at DATETIME NULL,
       revoked_at DATETIME NULL,
       UNIQUE KEY idx_api_keys_uuid (uuid),
       UNIQUE KEY idx_api_keys_value (key_value),
       KEY idx_api_keys_source (source_id),
       KEY idx_api_keys_prefix (key_prefix),
       KEY idx_api_keys_active (is_active),
       CONSTRAINT fk_api_keys_source FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

   -- Seed an initial bootstrap source so existing rows can backfill
   -- and new instances have something to start from. The installer
   -- will either rename this or create additional sources on first
   -- run, but the default row guarantees referential integrity.
   INSERT INTO sources (uuid, code, name, source_type, description, is_active)
   VALUES (UUID(), 'bootstrap', 'Bootstrap Source', 'other',
           'Initial source created by the installer. Rename or create additional sources as needed.',
           TRUE);

``migrations/015_contact_and_communication_source_id.sql``

.. code-block:: sql

   -- Add first_seen_source_id to contacts
   ALTER TABLE contacts ADD COLUMN first_seen_source_id BIGINT UNSIGNED NULL AFTER contact_type_id;
   UPDATE contacts
     SET first_seen_source_id = (SELECT id FROM sources WHERE code = 'bootstrap')
     WHERE first_seen_source_id IS NULL;
   ALTER TABLE contacts MODIFY COLUMN first_seen_source_id BIGINT UNSIGNED NOT NULL;
   ALTER TABLE contacts ADD KEY idx_contacts_first_seen_source (first_seen_source_id);
   ALTER TABLE contacts ADD CONSTRAINT fk_contacts_first_seen_source
       FOREIGN KEY (first_seen_source_id) REFERENCES sources(id) ON DELETE RESTRICT;

   -- Add source_id to communications
   ALTER TABLE communications ADD COLUMN source_id BIGINT UNSIGNED NULL AFTER id;
   UPDATE communications
     SET source_id = (SELECT id FROM sources WHERE code = 'bootstrap')
     WHERE source_id IS NULL;
   ALTER TABLE communications MODIFY COLUMN source_id BIGINT UNSIGNED NOT NULL;
   ALTER TABLE communications ADD KEY idx_communications_source (source_id);
   ALTER TABLE communications ADD CONSTRAINT fk_communications_source
       FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE RESTRICT;

   -- Re-create v_contact_summary and v_contact_last_order so they
   -- surface the first_seen_source information. Preserve all existing
   -- columns; add first_seen_source_code and first_seen_source_name
   -- as new columns at the end of each view.
   DROP VIEW IF EXISTS v_contact_summary;
   DROP VIEW IF EXISTS v_contact_last_order;
   -- [re-create both views here with the extra JOINs]

``migrations/016_crossproject_channel_types.sql``

.. code-block:: sql

   INSERT INTO channel_types (code, label, description, sort_order) VALUES
     ('web_form',            'Web Form',            'Contact form submission from a website',                  10),
     ('appointment_request', 'Appointment Request', 'Online appointment request (pre-scheduler)',              11),
     ('booking_started',     'Booking Started',     'User started the booking flow',                           12),
     ('booking_completed',   'Booking Completed',   'Appointment booking confirmed',                           13),
     ('booking_cancelled',   'Booking Cancelled',   'Appointment cancelled after booking',                     14),
     ('phone_click',         'Phone Click',         'User clicked a tel: link on a website',                   15),
     ('book_click',          'Book Click',          'User clicked a CTA linking to the booking page',          16),
     ('form_submit',         'Form Submit',         'Generic form submission (fallback when no specific type)',17),
     ('scroll_depth',        'Scroll Depth',        'User scrolled past a tracked milestone (50/75/90)',       18),
     ('page_view',           'Page View',           'High-intent page view (service page, pricing page)',      19);

``migrations/017_v_events_by_source_view.sql``

.. code-block:: sql

   CREATE OR REPLACE VIEW v_events_by_source AS
   SELECT
       c.id               AS communication_id,
       c.uuid             AS communication_uuid,
       s.code             AS source_code,
       s.name             AS source_name,
       s.source_type      AS source_type,
       s.domain           AS source_domain,
       ct.code            AS channel_code,
       ct.label           AS channel_label,
       c.direction,
       c.occurred_at,
       c.subject,
       c.body,
       c.external_message_id,
       c.contact_id,
       co.uuid            AS contact_uuid,
       co.first_name,
       co.last_name,
       co.external_refs_json,
       c.created_at,
       c.created_by
   FROM communications c
   JOIN sources s        ON s.id = c.source_id
   JOIN channel_types ct ON ct.id = c.channel_type_id
   LEFT JOIN contacts co ON co.id = c.contact_id;

``migrations/018_schema_migrations_tracking.sql``

.. code-block:: sql

   -- Tracks which migrations have been applied so the installer's
   -- bootstrap-migrations.sh can be idempotent. Applied FIRST on
   -- fresh installs — the runner special-cases its own creation.
   CREATE TABLE IF NOT EXISTS _schema_migrations (
       version VARCHAR(255) PRIMARY KEY,
       applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

API middleware changes
======================================================================

Update ``api/app/middleware/auth.py`` (or wherever the current API
key check lives):

1. On every request, read the ``X-API-Key`` header.
2. **Special-case the root key:** if ``X-API-Key`` equals the
   ``CLIENTHUB_ROOT_API_KEY`` env var, set request context
   ``source_id = None`` (meaning: admin, unrestricted, can manage
   sources and keys).
3. Otherwise, do a
   ``SELECT source_id FROM api_keys WHERE key_value = ? AND is_active = 1 AND revoked_at IS NULL``.
4. If no row found, return 401.
5. If found, set the request context ``source_id`` and update
   ``last_used_at`` asynchronously (fire-and-forget; don't block
   the request).
6. Expose the ``source_id`` as a FastAPI dependency that every
   router can ``Depends(...)`` on.

Write-time source stamping
======================================================================

Every router that creates contacts or communications must
auto-stamp the source_id from the request context:

- ``POST /api/v1/contacts`` — if ``first_seen_source_id`` is not
  provided in the request body, set it to the request's
  ``source_id``. Root key: require it in the body or default to
  ``bootstrap``.
- ``POST /api/v1/communications`` — same for ``source_id``.
- Webhook endpoints (``/webhooks/invoiceninja``,
  ``/webhooks/chatwoot``) use a dedicated source key configured
  in their respective integrations. The webhook handlers look up
  the appropriate source by code if needed.

**Source spoofing prevention:** the middleware must reject any
write from a non-root key that explicitly sets ``source_id`` to a
value different from the key's own source. Root key can set any
source_id.

Read-time source scoping
======================================================================

**Reads are not scoped by source.** Source-key-authenticated GETs
can query any contact or communication in the DB. This is
intentional — all data in a single client-hub instance belongs
to one company and should be queryable by any integration that
company runs.

The only exception is the admin routes (below), which require the
root key.

New admin endpoints (root-key-only)
======================================================================

Add a new router at ``api/app/routers/admin.py``:

- ``POST /api/v1/admin/sources`` — create a new source
- ``GET /api/v1/admin/sources`` — list all sources
- ``GET /api/v1/admin/sources/{uuid}`` — get one source
- ``PUT /api/v1/admin/sources/{uuid}`` — update source metadata
- ``DELETE /api/v1/admin/sources/{uuid}`` — soft-delete
  (``is_active = 0``); do NOT hard-delete because existing
  contacts and communications FK to it
- ``POST /api/v1/admin/sources/{uuid}/api-keys`` — create a new
  API key for that source
- ``GET /api/v1/admin/sources/{uuid}/api-keys`` — list keys
  (shows key_prefix only, never key_value)
- ``DELETE /api/v1/admin/api-keys/{uuid}`` — revoke a key (soft
  delete, sets ``is_active = 0`` and ``revoked_at``)

These endpoints require the root API key — reject all other keys
with 403 and a clear message.


**********************************************************************
Extended data collection + PII handling
**********************************************************************

Brad's explicit decision: store **real data**, not hashes. Richer
enrichment, better ad attribution, better customer follow-up.

What we collect and store
======================================================================

For every incoming event that can be tied to a contact:

- **Full name** (``contacts.first_name`` + ``contacts.last_name``)
  — when available
- **Email addresses** (``contact_emails`` with type + primary flag)
- **Phone numbers** (``contact_phones`` with type + primary flag)
- **Timestamps in UTC** (``communications.occurred_at``,
  ``contacts.created_at``) — all DATETIME columns MUST store UTC.
  The MariaDB container's timezone is set to ``UTC`` in the
  bundled compose.
- **Real IP address** (stored in
  ``external_refs_json.ip_address``)
- **User agent string** (``external_refs_json.user_agent``)
- **Referrer URL** (``external_refs_json.referrer``)
- **UTM parameters**
  (``external_refs_json.utm.{source,medium,campaign,term,content}``)
- **Source page** (``external_refs_json.source_page`` — the path
  like ``/services/dental-implants``)
- **GA4 client ID** (``external_refs_json.gtm_client_id``) when
  available

The ``source_id`` is NOT stored in ``external_refs_json``; it's a
proper column (Option B).

Formalized external_refs_json shape
======================================================================

.. code-block:: json

   {
     "source_page": "/services/dental-implants",
     "referrer": "https://www.google.com/",
     "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...",
     "ip_address": "71.68.131.185",
     "gtm_client_id": "GA1.2.1234567890.1234567890",
     "utm": {
       "source": "google",
       "medium": "organic",
       "campaign": "branded",
       "term": null,
       "content": null
     },
     "extra": {
       "form_name": "request-availability",
       "service_interest": "dental-implants"
     }
   }

The ``extra`` sub-object is a free-form escape hatch for
site-specific metadata. The rest of the keys are the convention.

PII and privacy implications
======================================================================

Storing real IPs and user agents creates PII-handling obligations
under GDPR/CCPA for any site that might serve EU/California
visitors. Brad has made the explicit decision to do this anyway.
The implementation session should:

1. **Document** the PII storage choice clearly in
   ``docs/Data-Privacy.rst`` (new file) with:

   - What fields are PII
   - Retention expectations (propose 2 years as a default and
     document how to change it)
   - Access controls (API keys are the only access path; the
     root key is the only way to delete)
   - How to run a deletion request (SQL example and/or admin
     endpoint recipe)
   - Why Brad chose this over hashing (richer enrichment, better
     ad attribution, better customer follow-up)

2. **Never log** full IPs, UAs, or emails to stdout or log files
   by default. The API should redact these in log output.

3. **Enforce TLS** for any public-facing deployment. The
   installer refuses to run in bundled+domain mode without Caddy
   + Let's Encrypt; refuses to bind to 0.0.0.0 on port 8800
   without a loud warning when no domain is provided.


**********************************************************************
Deliverable inventory
**********************************************************************

Complete list of files to create or modify. Order them in commits
by the logical grouping below.

New files
======================================================================

Infrastructure:

- ``scripts/install.sh`` — the one-line installer (~400 lines)
- ``scripts/uninstall.sh`` — symmetric removal (preserves backups)
- ``scripts/backup.sh`` — cron-callable, dumps + rotates
  (7 day default)
- ``scripts/bootstrap-migrations.sh`` — idempotent migration
  runner
- ``scripts/generate-api-key.sh`` — helper for rotating / minting
  keys
- ``scripts/smoke-test.sh`` — post-install verification
- ``docker-compose.bundled.yml`` — MariaDB + client-hub-api +
  Caddy
- ``docker-compose.bundled-nodomain.yml`` — same, minus Caddy,
  exposes 8800 on the host (for installs without a domain)
- ``Caddyfile`` — reverse-proxy with auto-TLS

Schema (migrations applied in order):

- ``migrations/014_sources_and_api_keys.sql``
- ``migrations/015_contact_and_communication_source_id.sql``
- ``migrations/016_crossproject_channel_types.sql``
- ``migrations/017_v_events_by_source_view.sql``
- ``migrations/018_schema_migrations_tracking.sql`` — applied
  first on fresh installs; the bootstrap runner special-cases
  its own creation

API code (under ``api/app/``):

- ``api/app/models/source.py`` — SQLAlchemy ORM model
- ``api/app/models/api_key.py`` — SQLAlchemy ORM model
- ``api/app/schemas/source.py`` — Pydantic request/response
- ``api/app/schemas/api_key.py`` — Pydantic request/response
- ``api/app/routers/admin.py`` — admin router (root-key-only)
- ``api/app/services/source_context.py`` — FastAPI dependency
  that resolves the current request's ``source_id`` from the
  API key
- Update ``api/app/middleware/auth.py`` — new lookup-based auth
- Update ``api/app/main.py`` — include the new admin router
- Update every existing router that creates contacts or
  communications to auto-stamp ``source_id`` /
  ``first_seen_source_id``

Tests:

- ``api/tests/test_sources.py`` — CRUD + listing (root-key-only)
- ``api/tests/test_api_keys.py`` — create, list, revoke
- ``api/tests/test_multi_source_attribution.py`` — critical:

  1. Create two sources (A and B) with separate API keys
  2. Use source A's key to create a contact — assert
     ``contacts.first_seen_source_id = A``
  3. Use source B's key to create a communication on that contact
     — assert ``communications.source_id = B``
  4. Use source A's key to read that communication — assert it's
     returned (shared read across sources)
  5. Use source A's key to create another communication —
     assert it's stamped with A
  6. Use source A's key to attempt creating a communication with
     ``source_id = B`` in the body — assert it's either rejected
     (403) or silently overridden with A
  7. Use the root key to read everything — assert full access

- Update every existing test to pass the default bootstrap
  source's API key or the root key

Documentation:

- ``docs/Deployment.rst`` — user-facing install + operations
  guide with the one-liner at the top
- ``docs/Cross-Project-Integration.rst`` — copy-paste guide for
  Next.js sites wanting to push events (includes a full
  reference ``lib/client-hub.ts`` module)
- ``docs/Multi-Source.rst`` — architectural explanation of the
  sources + api_keys model, including the explicit note that
  client-hub remains single-DB-per-company and sources are for
  within-company system attribution only
- ``docs/Data-Privacy.rst`` — PII handling policy
- ``docs/Upgrade.rst`` — how to safely upgrade an installed
  instance

Modified files
======================================================================

- ``CLAUDE.md`` — major update: new Deployment section, updated
  architecture, multi-source facts (preserving the single-tenant
  note)
- ``README.rst`` — add the one-liner install command
  front-and-center
- ``.env.example`` — add all new vars (see Environment variables
  below)
- ``TODO.rst`` — mark "Automated database backups" and "Expose
  API via Nginx Proxy Manager with SSL" as done via the new
  installer + Caddy. Add any new items discovered during
  implementation.
- ``CHANGELOG.rst`` — comprehensive entry
- ``docker-compose.yml`` — keep this as the "development"
  compose (unchanged behavior, still depends on external
  ``my-main-net``). The new bundled compose is a separate file.
- ``api/app/config.py`` — add ``clienthub_root_api_key`` setting,
  standardize on ``db_user: clienthub`` default
- ``.github/workflows/ci.yml`` — add the new migrations to the
  test job, add shellcheck for the bash scripts


**********************************************************************
Installer behavior spec
**********************************************************************

Target OS
======================================================================

- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS
- Debian 12 (Bookworm)+

Any other distro: refuse to run with a clear error message.

Invocation
======================================================================

**Primary (interactive, public repo):**

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh | sudo bash

**Non-interactive (for CI/automation):**

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh \
     | sudo bash -s -- \
     --mode bundled \
     --domain client-hub-complete-dental-care.onlinesalessystems.com \
     --admin-email admin@onlinesalessystems.com \
     --first-source-code complete_dental_care_website \
     --first-source-name "Complete Dental Care Website" \
     --sdks typescript \
     --non-interactive

Source download modes
======================================================================

The installer must support two download paths for the repo itself:

1. **git clone** (default):
   ``git clone https://github.com/stancel/client-hub /opt/client-hub``
   Works now that the repo is public.

2. **tarball fallback:** set ``CLIENTHUB_TARBALL_URL`` env var to
   a pre-signed or temporary URL; installer ``curl``s it and
   extracts to ``/opt/client-hub``. Works with private repos or
   pinned versions without setting up deploy keys.

The installer auto-detects: if ``CLIENTHUB_TARBALL_URL`` is set,
use that; otherwise fall back to ``git clone``.

Prereq detection + installation
======================================================================

- Verify running as root (or re-exec with sudo)
- Detect OS via ``/etc/os-release``
- Install via apt: ``ca-certificates``, ``curl``, ``openssl``,
  ``gnupg``, ``ufw``, ``mariadb-client``, ``cron``, ``git``
- Install Docker via the official convenience script if not
  already installed: ``curl -fsSL https://get.docker.com | sh``
- Install docker-compose plugin (``docker-compose-plugin``)
- Verify ``docker compose version`` works

User + directory setup
======================================================================

- Create system user ``clienthub`` (no shell, no home):
  ``useradd --system --no-create-home --shell /usr/sbin/nologin clienthub``
- Add ``clienthub`` to the ``docker`` group
- Create ``/opt/client-hub`` owned by ``clienthub:clienthub``
  mode 0750
- Create ``/opt/client-hub/backups`` owned by
  ``clienthub:clienthub`` mode 0700
- Create ``/var/log/client-hub`` owned by ``clienthub:clienthub``
  mode 0750

Interactive prompts
======================================================================

In interactive mode, prompt for:

1. Domain name (optional — empty skips TLS)
2. Admin email (required if domain provided — for Let's Encrypt)
3. First source code (slug) — default ``bootstrap``, but strongly
   recommend the user provide something descriptive like
   ``complete_dental_care_website``
4. First source display name — default "Bootstrap Source"
5. SDK languages to generate: ``all`` / ``python`` / ``php`` /
   ``typescript`` / ``none``
6. Deployment mode: ``bundled`` (default) / ``external``

In non-interactive mode, take all of these as flags. Defaults:

- ``--mode bundled``
- ``--sdks none`` (don't generate by default; slow step)
- No domain (skips TLS, exposes 8800 with a warning)
- ``--first-source-code bootstrap``

Hardware sizing check
======================================================================

Before proceeding with ``bundled`` mode, check available RAM and
disk:

- ``--mode bundled``: needs at least **1.0 GB available RAM** and
  **10 GB free disk**. Warn if less. **Refuse to run** if below
  512 MB RAM or 5 GB disk with a clear message directing the user
  to resize the VPS.
- ``--mode external``: needs at least **512 MB RAM** and 5 GB
  disk (API + Caddy only).

Target sizing recommendations (print during install):

- **Minimum viable:** 1 vCPU / 2 GB RAM / 25 GB SSD
  (DigitalOcean $12/mo)
- **Comfortable:** 2 vCPU / 4 GB RAM / 50 GB SSD
  (DigitalOcean $24/mo)
- **External DB mode:** 1 vCPU / 1 GB RAM / 25 GB SSD (lighter)

Secret generation
======================================================================

- ``MARIADB_ROOT_PASSWORD``: ``openssl rand -hex 32``
- ``DB_PASSWORD`` (for the ``clienthub`` MariaDB user):
  ``openssl rand -hex 32``
- ``CLIENTHUB_ROOT_API_KEY``: ``openssl rand -hex 32``
- First-source API key: ``openssl rand -hex 32`` (inserted into
  the ``api_keys`` table, linked to the first source)

Never print any secret to stdout except once, at the very end, in
the install summary.

Compose up + migrations
======================================================================

1. ``docker compose -f docker-compose.bundled.yml pull`` (pre-pull
   images for a clean single-step ``up``)
2. ``docker compose -f docker-compose.bundled.yml up -d`` (brings
   up MariaDB, API, Caddy — or nodomain variant if no domain)
3. Wait for MariaDB healthcheck (``mariadb-admin ping`` in a loop
   with a 60s timeout)
4. Create the ``clienthub`` MariaDB user with the appropriate
   GRANT on the database (via a root-authenticated ``mariadb``
   session inside the container) — unless the bundled compose's
   ``MARIADB_USER`` env var handles this (preferred; simpler)
5. Run ``scripts/bootstrap-migrations.sh`` — this creates the
   ``_schema_migrations`` tracking table if needed, then applies
   every ``migrations/*.sql`` that hasn't already been applied
6. Verify no migration failed; abort install if any did
7. If ``--first-source-code`` is not ``bootstrap``, insert the
   new source row and rename/deactivate the seeded bootstrap row
   as appropriate (or keep both — Brad's call)
8. Insert the first-source API key into ``api_keys``
9. Restart the API container so it picks up the populated DB
10. Smoke test: ``curl -f http://127.0.0.1:8800/api/v1/health``
    must return 200. Retry up to 30s.

Firewall
======================================================================

- ``ufw default deny incoming``
- ``ufw default allow outgoing``
- ``ufw allow 22/tcp``
- If domain provided: ``ufw allow 80/tcp`` + ``ufw allow 443/tcp``
- If no domain: ``ufw allow 8800/tcp`` + print a loud warning
- ``ufw --force enable``

Backup cron
======================================================================

Install ``/etc/cron.daily/client-hub-backup`` (symlink to
``/opt/client-hub/scripts/backup.sh``). The backup script:

1. ``docker compose exec -T mariadb mariadb-dump ... | gzip > /opt/client-hub/backups/clienthub-$(date -u +%Y%m%d-%H%M%S).sql.gz``
2. Deletes backups older than 7 days
3. Logs to ``/var/log/client-hub/backup.log``
4. Chmod 0600 on the resulting dump file, owned by ``clienthub``

SDK generation (optional)
======================================================================

If ``--sdks`` is not ``none``, after the API is healthy the
installer runs ``scripts/generate-sdks.sh <language>`` which
creates SDKs under ``/opt/client-hub/sdks/``. Print the paths in
the install summary.

Install summary
======================================================================

At the very end, write ``/opt/client-hub/.install-summary``
(mode 0600, owned by ``clienthub``) and also echo it to stdout:

.. code-block:: text

   =====================================================
   Client Hub Installation Complete
   =====================================================

   Install path:  /opt/client-hub
   Mode:          bundled
   Domain:        client-hub-complete-dental-care.onlinesalessystems.com
   API URL:       https://client-hub-complete-dental-care.onlinesalessystems.com
   Swagger UI:    https://client-hub-complete-dental-care.onlinesalessystems.com/docs

   Credentials (SAVE THESE — they are also in
   /opt/client-hub/.install-summary, owned by clienthub mode 0600):

     Root API key (admin, cross-source):
       <64-char hex>

     First source code:
       complete_dental_care_website

     First source API key (write, source-scoped):
       <64-char hex>

     MariaDB root password:
       <64-char hex>

     MariaDB clienthub password:
       <64-char hex>

   Next steps:

     1. Save these credentials in a password manager immediately.
     2. Test the API (admin):
        curl -H "X-API-Key: <root key>" https://.../api/v1/health
     3. Test the API (source):
        curl -H "X-API-Key: <first source key>" https://.../api/v1/contacts
     4. Create additional sources via the admin API as needed.
     5. Start pushing events from your Next.js sites.

   Logs:
     docker compose -f /opt/client-hub/docker-compose.bundled.yml logs -f

   Backups: /opt/client-hub/backups/ (nightly, 7-day retention)

   Uninstall: sudo /opt/client-hub/scripts/uninstall.sh


**********************************************************************
Bundled docker-compose.yml
**********************************************************************

The new file ``docker-compose.bundled.yml`` should include three
services: mariadb, client-hub-api, caddy. Sketch (the
implementation session will flesh this out):

.. code-block:: yaml

   services:
     mariadb:
       image: mariadb:12.2
       container_name: clienthub-mariadb
       restart: unless-stopped
       environment:
         MARIADB_ROOT_PASSWORD: ${MARIADB_ROOT_PASSWORD}
         MARIADB_DATABASE: ${DB_NAME:-clienthub}
         MARIADB_USER: ${DB_USER:-clienthub}
         MARIADB_PASSWORD: ${DB_PASSWORD}
         TZ: UTC
       volumes:
         - ./data/mariadb:/var/lib/mysql
       healthcheck:
         test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
         interval: 10s
         timeout: 5s
         retries: 5
       networks:
         - clienthub

     client-hub-api:
       build:
         context: ./api
         dockerfile: Dockerfile
       container_name: clienthub-api
       restart: unless-stopped
       depends_on:
         mariadb:
           condition: service_healthy
       environment:
         DB_HOST: mariadb
         DB_PORT: 3306
         DB_NAME: ${DB_NAME:-clienthub}
         DB_USER: ${DB_USER:-clienthub}
         DB_PASSWORD: ${DB_PASSWORD}
         CLIENTHUB_ROOT_API_KEY: ${CLIENTHUB_ROOT_API_KEY}
         API_HOST: 0.0.0.0
         API_PORT: 8800
         TZ: UTC
       networks:
         - clienthub

     caddy:
       image: caddy:2
       container_name: clienthub-caddy
       restart: unless-stopped
       depends_on:
         - client-hub-api
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./Caddyfile:/etc/caddy/Caddyfile:ro
         - ./data/caddy:/data
         - ./data/caddy-config:/config
       environment:
         DOMAIN: ${DOMAIN:-localhost}
         ADMIN_EMAIL: ${ADMIN_EMAIL}
       networks:
         - clienthub

   networks:
     clienthub:
       driver: bridge

**The no-domain variant** (``docker-compose.bundled-nodomain.yml``)
drops the Caddy service entirely and exposes ``client-hub-api``
port 8800 directly to the host. The installer picks which compose
file to use based on whether a domain was supplied.

Caddyfile
======================================================================

.. code-block:: text

   {$DOMAIN} {
       encode gzip
       reverse_proxy client-hub-api:8800

       log {
           output file /var/log/caddy/access.log
           format json
       }
   }

Caddy handles TLS automatically via Let's Encrypt. No manual cert
management.


**********************************************************************
Environment variables (new .env.example)
**********************************************************************

.. code-block:: bash

   # ==============================================================
   # Client Hub - Environment Variables
   # ==============================================================
   # Generated by scripts/install.sh. Mode 0600, owned by clienthub.

   # --------------------------------------------------------------
   # Deployment mode (bundled | external)
   # --------------------------------------------------------------
   MODE=bundled

   # --------------------------------------------------------------
   # Domain and TLS (leave blank for plain-HTTP no-domain mode)
   # --------------------------------------------------------------
   DOMAIN=
   ADMIN_EMAIL=

   # --------------------------------------------------------------
   # Database. Passwords are auto-generated by install.sh via
   # `openssl rand -hex 32`. Never set these by hand.
   # --------------------------------------------------------------
   DB_NAME=clienthub
   DB_USER=clienthub
   DB_PASSWORD=REPLACED_BY_INSTALLER
   MARIADB_ROOT_PASSWORD=REPLACED_BY_INSTALLER

   # --------------------------------------------------------------
   # API root key (bypasses source context — admin access).
   # Used to manage sources and api_keys via /api/v1/admin/*.
   # Keep it secret. Auto-generated by install.sh.
   # --------------------------------------------------------------
   CLIENTHUB_ROOT_API_KEY=REPLACED_BY_INSTALLER

   # --------------------------------------------------------------
   # Timezone (must be UTC for consistency across integrations)
   # --------------------------------------------------------------
   TZ=UTC


**********************************************************************
Cross-project integration guide (reference lib/client-hub.ts)
**********************************************************************

The ``docs/Cross-Project-Integration.rst`` doc must include a full,
working, copy-pasteable ``lib/client-hub.ts`` module that any
Next.js site can drop in. The implementation session should write
the reference module based on this spec:

.. code-block:: typescript

   // lib/client-hub.ts
   //
   // Send conversion events to the client-hub Customer & Prospect
   // Intelligence system. Error-swallowing — never crashes caller.

   const CLIENTHUB_URL = process.env.CLIENTHUB_URL
     || "https://client-hub.example.com";
   const CLIENTHUB_API_KEY = process.env.CLIENTHUB_API_KEY || "";
   const CLIENTHUB_SOURCE_CODE = process.env.CLIENTHUB_SOURCE_CODE
     || "unknown";
   const TIMEOUT_MS = 3000;

   export type ConversionEvent =
     | "web_form"
     | "appointment_request"
     | "booking_started"
     | "booking_completed"
     | "booking_cancelled"
     | "phone_click"
     | "book_click"
     | "form_submit"
     | "scroll_depth"
     | "page_view";

   export interface LogConversionInput {
     event: ConversionEvent;
     email?: string;
     phone?: string;
     firstName?: string;
     lastName?: string;
     subject?: string;
     body?: string;
     sourcePage?: string;
     referrer?: string;
     userAgent?: string;
     ipAddress?: string;
     gtmClientId?: string;
     utm?: {
       source?: string;
       medium?: string;
       campaign?: string;
       term?: string;
       content?: string;
     };
     extra?: Record<string, unknown>;
   }

   export async function logConversion(
     input: LogConversionInput
   ): Promise<void> {
     if (!CLIENTHUB_API_KEY) {
       console.warn("[client-hub] CLIENTHUB_API_KEY not set; skipping");
       return;
     }

     const occurredAt = new Date().toISOString();
     const externalRefs = {
       source_page: input.sourcePage,
       referrer: input.referrer,
       user_agent: input.userAgent,
       ip_address: input.ipAddress,
       gtm_client_id: input.gtmClientId,
       utm: input.utm,
       extra: input.extra,
     };

     const controller = new AbortController();
     const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

     try {
       // 1. Create / upsert contact. The API auto-stamps
       //    first_seen_source_id from our X-API-Key.
       const contactRes = await fetch(
         `${CLIENTHUB_URL}/api/v1/contacts`,
         {
           method: "POST",
           headers: {
             "Content-Type": "application/json",
             "X-API-Key": CLIENTHUB_API_KEY,
           },
           body: JSON.stringify({
             contact_type: "lead",
             first_name: input.firstName ?? "",
             last_name: input.lastName ?? "",
             emails: input.email
               ? [{ address: input.email, is_primary: true }]
               : [],
             phones: input.phone
               ? [{ number: input.phone, is_primary: true }]
               : [],
             external_refs_json: externalRefs,
           }),
           signal: controller.signal,
         }
       );

       if (!contactRes.ok) {
         console.warn(
           `[client-hub] contact create failed: ${contactRes.status}`
         );
         return;
       }

       const contact = (await contactRes.json()) as { uuid: string };

       // 2. Log the communication event. The API auto-stamps
       //    source_id from our X-API-Key.
       await fetch(`${CLIENTHUB_URL}/api/v1/communications`, {
         method: "POST",
         headers: {
           "Content-Type": "application/json",
           "X-API-Key": CLIENTHUB_API_KEY,
         },
         body: JSON.stringify({
           contact_uuid: contact.uuid,
           channel: input.event,
           direction: "inbound",
           occurred_at: occurredAt,
           subject: input.subject,
           body: input.body,
         }),
         signal: controller.signal,
       });
     } catch (err) {
       console.warn(`[client-hub] event failed:`, err);
     } finally {
       clearTimeout(timeoutId);
     }
   }

The implementation session should harden this: add exponential
backoff retry (max 3, jittered), type the responses properly using
the generated TypeScript SDK types where convenient, and export
``logConversionBackground`` for callers that don't await.


**********************************************************************
Standardized channel_types vocabulary
**********************************************************************

Full list of the new channel_types rows (migration 016). These are
the canonical codes every Web Factory site uses.

.. list-table::
   :header-rows: 1
   :widths: 22 25 53

   * - code
     - label
     - Meaning
   * - ``web_form``
     - Web Form
     - Contact form submission from a website
   * - ``appointment_request``
     - Appointment Request
     - Online appointment request (pre-scheduler-integrated era)
   * - ``booking_started``
     - Booking Started
     - User started the booking flow (selected a service)
   * - ``booking_completed``
     - Booking Completed
     - Appointment booking confirmed end-to-end
   * - ``booking_cancelled``
     - Booking Cancelled
     - Appointment cancelled after booking
   * - ``phone_click``
     - Phone Click
     - User clicked a ``tel:`` link on a website
   * - ``book_click``
     - Book Click
     - User clicked a CTA linking to the booking page
   * - ``form_submit``
     - Form Submit
     - Generic form submission (fallback)
   * - ``scroll_depth``
     - Scroll Depth
     - User scrolled past a tracked milestone (50/75/90%)
   * - ``page_view``
     - Page View
     - High-intent page view (service page, pricing page)


**********************************************************************
Security requirements checklist
**********************************************************************

- [ ] All secrets auto-generated via ``openssl rand -hex 32``
- [ ] No secret ever hardcoded in any file in the repo
- [ ] No secret ever echoed to stdout except once in the install
  summary
- [ ] ``/opt/client-hub/.env`` mode 0600, owned by ``clienthub``
- [ ] ``/opt/client-hub/.install-summary`` mode 0600, owned by
  ``clienthub``
- [ ] ``/opt/client-hub/backups/`` mode 0700, owned by
  ``clienthub``
- [ ] Docker socket never exposed to containers
- [ ] UFW configured before any services are publicly reachable
- [ ] Caddy handles TLS automatically — no manual cert management
- [ ] MariaDB container binds only to the Docker internal network
  (never 0.0.0.0) unless ``--mode external`` is being used or the
  user has explicitly added a ``docker-compose.override.yml``
- [ ] API root key is documented as a high-sensitivity credential
  with rotation instructions in ``docs/Upgrade.rst``
- [ ] Full IPs, UAs, emails, and phone numbers are never logged at
  INFO level — DEBUG only, with a warning in the deployment doc
- [ ] ``docs/Data-Privacy.rst`` covers the PII storage decision
  and deletion procedure
- [ ] Rate limiting on the admin endpoints (at minimum, a note in
  the Caddyfile explaining how to add it later)
- [ ] Source-stamping cannot be spoofed: a non-root key attempting
  to write with a different ``source_id`` is rejected or
  overridden

**API key storage decision:** keys are stored as plain values in
``api_keys.key_value``, not hashed. Rationale: if the DB is
compromised, the attacker already has all the data the keys would
protect — hashing adds complexity without meaningful
defense-in-depth in this specific context. The column is indexed
for fast lookup. ``key_prefix`` is stored separately so admin
tooling can show ``clienthub_abc12345...`` without exposing the
full key. Document this decision in ``docs/Multi-Source.rst``.


**********************************************************************
Testing requirements
**********************************************************************

The implementation session must verify all of the following before
considering the work done.

Unit / integration tests
======================================================================

- All 63 existing tests pass after schema changes (updated to pass
  ``source_id`` where needed or use the bootstrap source's API
  key / root key)
- New tests for the ``admin/sources`` CRUD endpoints
- New tests for the ``admin/sources/{uuid}/api-keys``
  create/list/revoke endpoints
- **Critical:** new ``test_multi_source_attribution.py`` per the
  spec in the "Tests" sub-section above
- ``pytest api/tests/ -v`` must pass with 0 failures

Lint
======================================================================

- ``ruff check api/app/ api/tests/`` clean
- ``rstcheck --report-level warning docs/*.rst CHANGELOG.rst
  TODO.rst README.rst`` clean
- ``shellcheck scripts/*.sh`` clean

Installer smoke test (on a fresh VM)
======================================================================

Ideally spin up a fresh Ubuntu 24.04 LTS VM (locally via multipass,
lima, or a throwaway DO droplet) and run the installer end-to-end:

- [ ] Installer detects OS correctly
- [ ] Installs Docker + prereqs without errors
- [ ] Creates ``clienthub`` system user
- [ ] Clones / downloads the repo
- [ ] Generates all secrets
- [ ] Brings up the compose stack
- [ ] Migrations apply cleanly (including the new 014–018)
- [ ] Migration runner is **idempotent**: running
  ``bootstrap-migrations.sh`` a second time is a no-op
- [ ] API health check returns 200
- [ ] A test event can be created via curl using the first
  source's API key and read back via ``v_events_by_source``
- [ ] Backup script produces a valid dump
- [ ] Uninstall script cleanly removes everything except backups

CI
======================================================================

- GitHub Actions CI must pass on the new branch before merge
- Add a ``shellcheck`` job for the new bash scripts


**********************************************************************
OpsInsights compatibility
**********************************************************************

Brad's OpsInsights SaaS product queries MariaDB instances over SSH
tunnels. ``docs/Deployment.rst`` must include an OpsInsights
section showing exactly how to tunnel in:

.. code-block:: bash

   # From the OpsInsights server (or any client):
   ssh -N -L 13306:127.0.0.1:3306 root@client-hub-complete-dental-care.onlinesalessystems.com

   # Then connect to 127.0.0.1:13306 as the clienthub user:
   mariadb -h 127.0.0.1 -P 13306 -u clienthub -p clienthub

**BUT:** the bundled compose does NOT bind MariaDB to the host's
3306 by default (security). For OpsInsights access, the
deployment doc should explain how to add a
``docker-compose.override.yml`` that exposes MariaDB to 127.0.0.1
(never 0.0.0.0):

.. code-block:: yaml

   # /opt/client-hub/docker-compose.override.yml
   services:
     mariadb:
       ports:
         - "127.0.0.1:3306:3306"


**********************************************************************
Success criteria — the implementation is done when
**********************************************************************

- [ ] One ``curl -fsSL ... | sudo bash`` command produces a
  running instance on a fresh Ubuntu 22.04 or 24.04 LTS VPS in
  under 10 minutes end-to-end
- [ ] The ``.install-summary`` file shows all four credentials and
  the API is responding on the configured domain with valid TLS
  (or port 8800 with a warning)
- [ ] A test POST to ``/api/v1/contacts`` using the first source's
  API key creates a contact visible in ``SELECT * FROM contacts``
  with ``first_seen_source_id`` set correctly
- [ ] A test POST to ``/api/v1/communications`` creates an event
  visible in ``SELECT * FROM v_events_by_source`` with
  ``source_id`` set correctly
- [ ] All existing tests pass in CI after schema changes
- [ ] New ``test_multi_source_attribution.py`` passes
- [ ] ``shellcheck scripts/*.sh`` is clean
- [ ] Nightly backup produces a valid dump in
  ``/opt/client-hub/backups/``
- [ ] Uninstall script cleanly removes everything except backups
- [ ] Migration runner is idempotent (second run = no-op)
- [ ] Documentation is complete and the one-liner is in
  ``README.rst``
- [ ] ``docs/Multi-Source.rst`` clearly explains the within-company
  multi-source model and contrasts it with the single-tenant-
  per-company deployment model
- [ ] ``docs/Cross-Project-Integration.rst`` contains the full
  reference ``lib/client-hub.ts`` module


**********************************************************************
Post-installation plan (for reference — not your job)
**********************************************************************

After the implementation session ships this work, Brad (or the
parent Claude Code session in the dental care repo) will:

1. Deploy the installer to the already-provisioned DigitalOcean
   droplet at
   ``client-hub-complete-dental-care.onlinesalessystems.com``.
   Brad has confirmed SSH access as root on port 22.
2. Run the installer with:

   - ``--domain client-hub-complete-dental-care.onlinesalessystems.com``
   - ``--admin-email`` (Brad will provide)
   - ``--first-source-code complete_dental_care_website``
   - ``--first-source-name "Complete Dental Care Website"``
   - ``--sdks typescript``

3. Save the credentials to a password manager
4. Use the admin API to create additional sources as needed
   (scheduler, CTI, chatwoot, ads landing pages)
5. Add ``CLIENTHUB_URL``, ``CLIENTHUB_API_KEY``, and
   ``CLIENTHUB_SOURCE_CODE`` to the dental care site's
   ``.env.local`` on the VPS
6. Drop the reference ``lib/client-hub.ts`` module into the
   dental care site
7. Wire it into ``app/api/contact/route.ts``, the scheduler hook,
   and a new ``app/api/track/route.ts`` for client-side events
8. Deploy via the standard ``git pull + deploy.sh`` workflow
9. Verify a test form submission lands in ``v_events_by_source``
10. Repeat for Clever Orchid and every future Web Factory site


.. note::

   **Second pass:** See ``docs/Post-Deployment-Fixes-Prompt.rst`` for
   fixes and improvements discovered during the first real production
   deployment.
    using the same pattern (each company gets its own client-hub
    instance on its own droplet)


**********************************************************************
References
**********************************************************************

- ``~/Sites/complete-dental-care-nextjs/docs/Growth-Opportunities.rst``
- ``~/Sites/complete-dental-care-nextjs/docs/Google-Business-Profile-Setup.rst``
- ``~/Sites/complete-dental-care-nextjs/docs/Conversion-Tracking-Plan.rst``
- ``~/docker/client-hub/CLAUDE.md``
- ``~/docker/client-hub/docs/api-design.rst``
- ``~/docker/client-hub/docs/data-model.rst``
- Ollama install script pattern (reference for the one-liner UX):
  https://ollama.com/install.sh
- Caddy docs for Let's Encrypt:
  https://caddyserver.com/docs/automatic-https
- MariaDB Docker Hub: https://hub.docker.com/_/mariadb
