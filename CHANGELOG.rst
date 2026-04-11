.. _client-hub-changelog:

######################################################################
Client Hub — Changelog
######################################################################

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
