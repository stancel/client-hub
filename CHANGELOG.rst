.. _client-hub-changelog:

######################################################################
Client Hub — Changelog
######################################################################

.. _client-hub-changelog-2026-04-22:

2026-04-22 — README: Prominent One-Line Installer Section
==========================================================================

The one-line ``curl | sudo bash`` installer (``scripts/install.sh``,
shipped in Phase 8) was discoverable only from ``CLAUDE.md`` and the
``docs/Deployment.rst`` guide — there was no mention in ``README.rst``,
which is the first thing anyone provisioning a new VPS looks at. Fixed.

- ``README.rst`` — New **One-Line Installer** chapter placed directly
  after the Overview (above Quick Info) so it is the first actionable
  thing after the project intro. Includes the interactive one-liner,
  the non-interactive form with all flags, and a flag reference table
  (``--mode``, ``--domain``, ``--admin-email``, ``--first-source-code``,
  ``--first-source-name``, ``--sdks``, ``--include-seed-data``,
  ``--install-dir``, ``--non-interactive``). Points to
  ``scripts/smoke-test.sh`` for post-install verification and
  ``docs/Deployment.rst`` for the full guide.
- Fixed stray "Embro idery" typo in the Overview paragraph.
- ``rstcheck --report-level warning README.rst`` — clean.

Installer URL still pointing at
``raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh``
per Brad — the repo will move eventually but not yet.

.. _client-hub-changelog-2026-04-18b:

2026-04-18 — OpsInsights TLS Fix Verified; Script Defaults to REQUIRE SSL
==========================================================================

Follow-up to the morning's 2026-04-18a entry. Between then and the end
of the day, Brad patched the OpsInsights ADOdb PDO SSL bug, deployed to
production, and verified the fix end-to-end against the Clever Orchid
Client Hub. The MariaDB general log captured 10+ TLS-encrypted
connections from OpsInsights egress IPs across both the production
SaaS path (``52.207.33.249``, AWS NAT Gateway) and the operator path
(``52.72.248.4``, OpenVPN) with zero plaintext attempts. ``REQUIRE SSL``
has been restored on the ``opsinsights_ro`` user. Full defense-in-depth
(IP allowlist + TLS + MariaDB auth + read-only grants) is back in force.

Script + docs updated to reflect the new reality:

- ``scripts/setup-opsinsights-tls.sh`` — ``REQUIRE_SSL`` default flipped
  from ``false`` to ``true``. Flag renamed: ``--require-ssl`` now a no-op
  (kept for back-compat); new ``--no-require-ssl`` for the rare case of
  onboarding against an older OpsInsights build. Verification step
  inverted accordingly — plaintext login must now be REJECTED in the
  default path.
- ``docs/OpsInsights-Direct-TLS-Plan.rst`` — Status line updated from
  "deviations from plan" to "fully verified". Old "Deviation — REQUIRE
  SSL dropped (interim)" section renamed to "History" and rewritten as
  a chronological narrative (interim drop → fix deployed → REQUIRE SSL
  restored → verified by client-side SSL-off test).
- ``docs/OpsInsights-Setup-Prompt.rst`` — Default run invocation no
  longer carries an interim caveat. Flag description inverted. Added
  an IP-role note (``52.207.33.249`` = NAT Gateway, ``52.72.248.4`` =
  OpenVPN) — these were originally labeled reversed in Brad's
  ``connect.opsinsights.com`` public docs, corrected after live
  traffic observation.
- IP role labels corrected throughout all three RST docs.

Clever Orchid Client Hub connection is now production-ready and fully
encrypted in transit. First customer Client Hub deployment closed out.

.. _client-hub-changelog-2026-04-18a:

2026-04-18 — OpsInsights SaaS Connection: Direct MySQL/TLS + IP Allowlist
==========================================================================

First real SaaS-integration pattern proven end-to-end against the
live Clever Orchid Client Hub VPS (``client-hub.cleverorchid.com``
/ ``165.245.130.39``). Two reusable integration plans documented,
one automation script written, first customer onboarded.

- New doc ``docs/OpsInsights-Direct-TLS-Plan.rst`` — the chosen
  connection pattern: MariaDB published on 3306 with a Let's
  Encrypt TLS cert (acquired via Caddy for a second vhost), iptables
  DOCKER-USER chain restricts inbound to the two OpsInsights exit
  IPs (``52.72.248.4`` / ``52.207.33.249``), read-only MariaDB user
  per customer. Full "As Implemented" section documents the actual
  deployed state on Clever Orchid, including the two production
  deviations: global ``require_secure_transport`` not set (would
  break the internal FastAPI connection), and ``REQUIRE SSL`` on
  the user was dropped at runtime because OpsInsights cannot
  negotiate TLS on MySQL connections due to a bug in its hardcoded
  ADOdb PDO driver. See the Deviation section for the full bug
  writeup and the two-line patch for the future OpsInsights
  modernization pass.
- New doc ``docs/OpsInsights-SSH-Tunnel-Plan.rst`` — the alternative
  integration pattern for read/write enrichment work. Preserved as
  a reference plan for when CTI ingest and InvoiceNinja join
  workflows need to write back to Client Hub. Not implemented yet.
- New doc ``docs/OpsInsights-Setup-Prompt.rst`` — the Knowledge
  Transfer prompt for future customer onboarding. Explains what the
  setup script does and why, prerequisites, run invocation,
  verification procedure on both sides, operational notes (cert
  renewal, rotation, revert), and the security model with
  compromise scenarios. Written so a fresh Claude Code session
  opened in ``/opt/client-hub/`` can execute the work end-to-end.
- New script ``scripts/setup-opsinsights-tls.sh`` — parameterized,
  idempotent automation of the whole flow. Adds the Caddyfile vhost,
  waits for ACME, stages the cert, patches
  ``docker-compose.bundled.yml`` for the 3306 publish + TLS mount,
  installs ``iptables-persistent`` and adds ``DOCKER-USER`` allow
  rules, recreates the MariaDB container, creates the read-only
  user, writes and emits credentials. Flags: ``--hostname``,
  ``--allow-ip`` (repeatable), ``--install-dir``, ``--mariadb-user``,
  ``--require-ssl`` (opt-in; default off pending OpsInsights fix),
  ``--rotate-password``, ``--dry-run``, ``--non-interactive``.
- First production customer: Clever Orchid Embroidery. 11 contacts
  / 13 communications as of onboarding. OpsInsights SaaS dashboard
  integration pending verification (the user retries the connection
  on the OpsInsights side before this commit is pushed).

.. _client-hub-changelog-2026-04-11f:

2026-04-11 — Documentation Sync Pass
======================================================================

End-of-day ``bring-repo-in-sync`` audit. No code changes; updated
docs to match current reality after Phases 8, 9, and 10 shipped
in rapid succession.

- ``CLAUDE.md`` — corrected counts (34 tables + 3 views;
  28 endpoint paths; 89 tests / 17 files; 17 prod migrations +
  1 dev); added Admin endpoint category (sources, api-keys,
  events); added note on the ``external_refs_json`` payload
  contract; expanded directory tree with bundled compose files
  and all 8 scripts; added ``v_events_by_source`` to views
  section; added production VPS URL and installer one-liner to
  Key Commands.
- ``README.rst`` — same count corrections in Quick Info,
  architecture diagram, Database Schema section, and Testing
  section; added Admin endpoint rows to API table; added
  ``api_keys``, ``sources``, ``_schema_migrations`` to the entity
  / lookup / system table lists; added ``v_events_by_source``;
  fully rewrote Project Structure tree to list all current
  files, directories, scripts, and docs.
- ``TODO.rst`` — noted current vs. initial counts in Phase 1,
  2, and 5 (schema grew from 31/2 to 34/3; tests from 63 to 89;
  paths from 23 to 28); added Phase 10 section for the
  ``external_refs_json`` fix.
- Claude Code project memory ``project_vision.md`` — updated
  phase list through Phase 10, reflected current counts, added
  notes on live VPS and the payload contract reference.

.. _client-hub-changelog-2026-04-11e:

2026-04-11 — Document external_refs_json Payload Contract
======================================================================

Documentation-only follow-up after the external_refs_json fix was
verified on the live dental care VPS. The server-side round-trip
proved the fix works, but surfaced that the dental care caller is
sending a thin payload and that ``booking.cancelled`` overwrites
``booking.created``.

- ``docs/Cross-Project-Integration.rst`` — added new section
  "external_refs_json Payload Contract" with the canonical JSON
  shape, a "don't shadow — merge" rule for scheduler update
  hooks, and a checklist new Web Factory sites (Clever Orchid,
  etc.) must satisfy before going live.
- ``docs/Dental-Care-Payload-Fix-Prompt.rst`` — new handoff prompt
  for the dental care Next.js session, covering: capturing
  request headers in the booking form server action, enriching
  ``extra`` with scheduler event details, fixing the
  ``booking.cancelled`` overwrite by appending a communication
  row instead of re-upserting the contact, and investigating the
  separate frontdesk cancellation email bug.

No code changes. Client-hub server side is unchanged from
``fa6bf2d``.

.. _client-hub-changelog-2026-04-11d:

2026-04-11 — Fix external_refs_json Data-Loss Bug
======================================================================

Fix for silent data loss on every ``POST /api/v1/contacts``
(and the same issue on Organization and Order create/update):

- **Root cause:** ``external_refs_json`` existed on the ORM models
  for Contact, Organization, and Order but was not declared on any
  Pydantic request schema, so FastAPI silently stripped the field
  from every create/update body before it reached the service
  layer. Every row created via the API had ``external_refs_json``
  NULL even when the client sent rich metadata.
- **Fix (Contact):** added
  ``external_refs_json: dict[str, Any] | None`` to
  ``ContactCreate`` / ``ContactUpdate``; GET/POST/PUT responses now
  return the parsed dict. Service layer serializes dict → JSON
  string on write, deserializes defensively on read (malformed
  rows log a warning and return ``None`` instead of 500).
- **Fix (Organization, Order):** same field added to their inline
  create/update Pydantic schemas; create and GET responses now
  round-trip the value.
- **Tests:** 7 new round-trip tests across
  ``test_contacts.py``, ``test_organizations.py``, and
  ``test_orders.py`` (with value, without value, update,
  deep-nested). ``pytest`` now reports **89 passed** (was 82).
- **Impact:** unblocks the dental care integration's
  ``lib/client-hub.ts`` payload (source_page, ip_address,
  user_agent, nested ``extra`` with appointment_id / service_name
  / staff_name / start_date / total_price) and future Eaglesoft
  sync metadata. Client-side code needs no changes.

.. _client-hub-changelog-2026-04-11c:

2026-04-11 — Post-Deployment Fixes and Hardening
======================================================================

Fixes from first real VPS deployment on
``client-hub-complete-dental-care.onlinesalessystems.com``:

- **Smoke test fix:** removed ``curl -sf`` (which suppresses 4xx
  status codes); now accepts 401 or 403 for unauthenticated access
- **Seed data separation:** moved ``012_seed_test_data.sql`` to
  ``migrations/dev/``; production installs no longer get test data.
  Use ``--with-seed-data`` flag for dev/CI. Updated CI workflow.
- **Cleanup script:** ``scripts/cleanup-test-data.sh`` for removing
  test data from already-contaminated production instances
- **Installer hardening:** DNS pre-flight check for TLS domains,
  ``--include-seed-data`` flag, ``docker-compose.override.yml.example``
  for OpsInsights access
- **Uninstall safety:** preserves ``.env`` and ``.install-summary``
  to ``/root/client-hub-saved/`` before deletion
- **Lookup fix:** phone and email lookup now return ALL contact
  phones and emails (not just the matched one)
- **Admin events endpoint:** ``GET /api/v1/admin/events`` with
  source_code, channel_code, date range filters (root-key-only)
- **82 tests passing** (was 78)

.. _client-hub-changelog-2026-04-11b:

2026-04-11 — Multi-Source Attribution + One-Line Installer
======================================================================

Major implementation based on Installation-Implementation-Prompt.rst:

**Goal A — One-Line Installer:**

- ``scripts/install.sh`` — Ollama-style ``curl|bash`` for Ubuntu/Debian
- ``scripts/uninstall.sh``, ``backup.sh``, ``bootstrap-migrations.sh``,
  ``smoke-test.sh``, ``generate-api-key.sh``
- ``docker-compose.bundled.yml`` (MariaDB + API + Caddy with auto-TLS)
- ``docker-compose.bundled-nodomain.yml`` (MariaDB + API, port 8800)
- ``Caddyfile`` with auto Let's Encrypt

**Goal B — Multi-Source Attribution:**

- Migrations 014-018: ``sources``, ``api_keys`` tables,
  ``first_seen_source_id`` on contacts, ``source_id`` on
  communications, cross-project channel_types (10 new Web Factory
  event codes), ``v_events_by_source`` view, ``_schema_migrations``
  tracking table
- New auth middleware: resolves X-API-Key to SourceContext (root key
  or per-source key)
- Admin router: CRUD for sources + API keys (root-key-only)
- Auto-stamps source_id on contact/communication creation
- Schema now: 34 tables + 3 views

**Goal C — Cross-Project Integration:**

- ``docs/Multi-Source.rst`` — sources vs marketing_sources
- ``docs/Deployment.rst`` — one-liner install guide
- ``docs/Cross-Project-Integration.rst`` — reference lib/client-hub.ts
- ``docs/Data-Privacy.rst`` — PII handling policy
- ``docs/Upgrade.rst`` — upgrade and key rotation guide

**Tests:** 78 passing (63 original + 15 new) across 16 test files

.. _client-hub-changelog-2026-04-11:

2026-04-11 — Full Documentation Refresh
======================================================================

- Rewrote README.rst to reflect complete project state: all 7 phases
  done, 23 endpoints, 63 tests, 3 SDKs, CI/CD pipeline, full
  architecture diagram, endpoint table, project structure tree
- Rewrote CLAUDE.md with current container info, all key commands,
  troubleshooting for the live API, SDK generation, CI/CD details
- Updated architecture.rst with live container layout and integration
  patterns (webhook, lookup, CRUD, direct SQL)
- All docs now accurately reflect the running system

.. _client-hub-changelog-2026-04-05h:

2026-04-05 — All API Endpoints Complete: 63 Tests, 23 Paths
======================================================================

- Implemented remaining routers: organizations, orders, invoices,
  payments, communications, webhooks (InvoiceNinja + Chatwoot),
  business settings
- 63 tests passing across 13 test files in 0.76 seconds
- 23 endpoint paths live on port 8800
- Full order lifecycle: create → add items → change status → invoice
  → record payments (auto-updates balance and status)
- Webhook handlers: InvoiceNinja payment sync, Chatwoot message
  identification and communication logging
- Container rebuilt and verified with curl

.. _client-hub-changelog-2026-04-05g:

2026-04-05 — Phase 5: API Server Live with 30 TDD Tests
======================================================================

- FastAPI server running in Docker on port 8800 (my-main-net)
- 30 tests passing across 6 test files (TDD, real DB)
- Implemented endpoints: health, phone/email lookup, contacts CRUD,
  conversion, marketing opt-outs, preferences, contact summary
- API key auth on all protected routes
- OpenAPI spec available at /openapi.json, Swagger at /docs
- Docker image built and container running as client-hub-api

.. _client-hub-changelog-2026-04-05f:

2026-04-05 — TDD Strategy and SDK Generation Plan
======================================================================

- Added TDD testing strategy to API design: every endpoint must have
  a test written before or alongside it, hitting real DB (not mocks)
- Added SDK generation section: auto-generate Python, PHP, TypeScript
  SDKs from OpenAPI spec via ``scripts/generate-sdks.sh``
- Expanded project structure with full test file listing (one per
  router module)
- Updated TODO.rst with Phase 6 (SDK Generation), Phase 7 (CI/CD
  Pipeline), and expanded Phase 5 with per-endpoint test requirements
- Added Future section to TODO.rst for planned integrations

.. _client-hub-changelog-2026-04-05e:

2026-04-05 — Data-First Reframing and Schema Enhancements
======================================================================

- Reframed project as **data-first customer intelligence microservice**
- Added ``marketing_opt_out_sms/email/phone`` boolean flags to contacts
- Added ``contact_preferences`` table (flexible key-value per contact)
- Created ``v_contact_summary`` view (holistic intelligence: lifetime
  value, order stats, communications, opt-outs, tags, sources)
- Created ``v_contact_last_order`` view (last order details per contact)
- Updated API design with preference, marketing, and intelligence
  endpoints
- Updated all docs (CLAUDE.md, data-model.rst, api-design.rst) to
  reflect data-first approach and new schema objects
- Schema now: 31 tables + 2 views (was 30 tables)

.. _client-hub-changelog-2026-04-05d:

2026-04-05 — Phase 3 Complete: Test Data and Validation
======================================================================

- Inserted realistic test data: 5 contacts (2 clients, 1 prospect,
  1 lead, 1 vendor), 2 organizations, 4 orders with line items,
  3 invoices, 3 payments, 7 communications, 3 notes
- Ran 11 validation queries — all passed with zero issues:
  FK integrity, orphan checks, CTI phone lookup, Chatwoot email
  lookup, prospect→client conversion, order→invoice→payment chain,
  junction tables, channel prefs, data provenance, status audit trail
- Created ``migrations/012_seed_test_data.sql`` for reproducibility

.. _client-hub-changelog-2026-04-05c:

2026-04-05 — Phase 1 Complete: Data Model Design
======================================================================

- Created comprehensive ``docs/data-model.rst`` (30 tables total)
- 17 entity tables: business_settings, contacts, organizations,
  contact_phones, contact_emails, contact_addresses, org_phones,
  org_emails, org_addresses, contact_channel_prefs, contact_notes,
  orders, order_items, order_status_history, invoices, payments,
  communications
- 2 junction tables: contact_tag_map, contact_marketing_sources
- 11 lookup tables: contact_types, phone_types, email_types,
  address_types, channel_types, marketing_sources, order_statuses,
  order_item_types, invoice_statuses, payment_methods, tags
- Full 3NF normalization analysis with documented denormalization
  decisions
- Corrected tenant model: single-tenant (one DB per business), not
  multi-tenant
- Development database: ``dev_schema`` on shared MariaDB

.. _client-hub-changelog-2026-04-05b:

2026-04-05 — Align with Shared MariaDB Infrastructure
======================================================================

- Removed standalone MariaDB container from ``docker-compose.yml``
- Switched to shared MariaDB 12.2.2 at ``~/docker/mariadb/`` on port
  3306 via ``my-main-net``
- Updated all docs to reference shared MariaDB and MySQL MCP Server
  (DBHub) for schema design workflow
- ``docker-compose.yml`` now a placeholder for Phase 2 API container
- Updated ``.env.example`` with simplified DB credentials

.. _client-hub-changelog-2026-04-05:

2026-04-05 — Initial Project Scaffolding
======================================================================

- Created project scaffolding with all standard files (CLAUDE.md,
  README.rst, CHANGELOG.rst, TODO.rst, docs/, .gitignore)
- Added ``docker-compose.yml`` (initially with standalone MariaDB)
- Added ``.env.example`` with database credential templates
- Created ``docs/architecture.rst`` with detailed architecture docs
- Created ``init/`` directory for SQL initialization scripts
- Project status: Phase 1 — Data model design
