.. _client-hub-readme:

######################################################################
Client Hub
######################################################################

.. _client-hub-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub is a **data-first customer intelligence microservice** — a
centralized, business-agnostic MariaDB data store that compiles and
enriches information from disparate systems into a single source of
truth for client data, prospect data, orders, invoicing, communication
history, and marketing intelligence.

The database schema is the primary product. The REST API is a
convenience layer. Both DB-level and API-level integration are valid
patterns depending on the task.

**Initial use case:** Embroidery business. **Future verticals:**
Dentist offices, lawn care, pressure washing, and other service
businesses. The schema is business-agnostic — one database per
business (single-tenant).

**GitHub:** https://github.com/stancel/client-hub

.. _client-hub-one-line-installer:

**********************************************************************
One-Line Installer
**********************************************************************

Provision a production VPS in a single command. Installs Docker,
clones the repo to ``/opt/client-hub``, runs migrations, and (in
bundled mode) brings up the API, MariaDB, and Caddy with automatic
Let's Encrypt TLS.

**Interactive (recommended for first-time installs):**

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh | sudo bash

**Non-interactive (scripted / CI):**

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh | sudo bash -s -- \
     --mode bundled \
     --domain client-hub.example.com \
     --admin-email admin@example.com \
     --first-source-code my_website \
     --first-source-name "My Website" \
     --sdks typescript \
     --non-interactive

**Installer flags:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Flag
     - Purpose
   * - ``--mode``
     - ``bundled`` (API + MariaDB + Caddy TLS) or
       ``bundled-nodomain`` (no TLS, IP-only)
   * - ``--domain``
     - Public hostname for the API (required for TLS)
   * - ``--admin-email``
     - Contact email for Let's Encrypt certificates
   * - ``--first-source-code``
     - Code for the first data source (e.g. ``my_website``)
   * - ``--first-source-name``
     - Human-readable name for the first data source
   * - ``--sdks``
     - Which SDK to generate post-install
       (``python``, ``php``, ``typescript``, or ``none``)
   * - ``--include-seed-data``
     - Seed dev/test data (omit for production)
   * - ``--install-dir``
     - Override install path (default: ``/opt/client-hub``)
   * - ``--non-interactive``
     - Skip prompts; use flags/defaults only

After install, verify with ``./scripts/smoke-test.sh``. See
``docs/Deployment.rst`` for the full deployment guide and
``scripts/install.sh`` for the complete source.

.. _client-hub-quick-info:

**********************************************************************
Quick Info
**********************************************************************

.. list-table::
   :widths: 30 70

   * - **App Location**
     - ``~/docker/client-hub/``
   * - **API URL**
     - http://10.0.1.220:8800
   * - **Swagger UI**
     - http://10.0.1.220:8800/docs
   * - **OpenAPI Spec**
     - http://10.0.1.220:8800/openapi.json
   * - **Database**
     - Shared MariaDB 12.2.2 at ``~/docker/mariadb/``
   * - **DB Host**
     - ``mariadb:3306`` (Docker DNS) / ``10.0.1.220:3306`` (host)
   * - **DB Name**
     - ``clienthub``
   * - **Schema**
     - 39 tables + 3 views (3NF normalized)
   * - **API Endpoints**
     - 36 paths across 12 routers
   * - **Test Suite**
     - 114 tests across 19 files
   * - **SDKs**
     - Python, PHP, TypeScript (auto-generated from OpenAPI)
   * - **CI/CD**
     - GitHub Actions (lint → test → build → SDK gen)
   * - **MCP Tools**
     - ``apisix-mysql`` (``execute_sql``, ``search_objects``)
   * - **Production deployment**
     - First instance live at
       ``client-hub-complete-dental-care.onlinesalessystems.com``
   * - **Status**
     - All phases complete. First live integration running
       (Complete Dental Care Next.js site).

.. _client-hub-architecture-summary:

**********************************************************************
Architecture
**********************************************************************

Client Hub uses the shared MariaDB instance at ``~/docker/mariadb/``
and runs a FastAPI container (``client-hub-api``) on ``my-main-net``.

.. code-block:: text

   External Systems
   ┌──────┬──────────┬──────┬────────┬───────┐
   │Chat- │Invoice-  │ CTI/ │Zammad  │Market-│
   │woot  │Ninja     │ SIP  │Support │ing    │
   └──┬───┴────┬─────┴──┬───┴───┬────┴──┬────┘
      │        │        │       │       │
      ▼        ▼        ▼       ▼       ▼
   ┌─────────────────────────────────────────┐
   │         client-hub-api (FastAPI)        │
   │         Port 8800 on my-main-net       │
   │    36 endpoints, API key auth          │
   │    Swagger UI at /docs                 │
   └─────────────────┬───────────────────────┘
                     │ SQLAlchemy (async)
                     ▼
   ┌─────────────────────────────────────────┐
   │     Shared MariaDB 12.2.2              │
   │     ~/docker/mariadb/ (port 3306)      │
   │     Database: clienthub               │
   │     36 tables + 3 views (3NF)          │
   └─────────────────────────────────────────┘

   Also accessible via:
   ├── Direct SQL (other containers on my-main-net)
   └── MCP tools (mysql-mcp-server / DBHub)

.. _client-hub-data-sources:

**********************************************************************
Data Sources
**********************************************************************

Client Hub compiles data from multiple disparate systems:

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - System
     - What It Provides
     - Integration Method
   * - InvoiceNinja
     - Invoicing, payments, contact updates
     - Webhook (``POST /api/v1/webhooks/invoiceninja``)
   * - Chatwoot
     - SMS/MMS, web chat, messaging
     - Webhook (``POST /api/v1/webhooks/chatwoot``)
   * - SIP/Phone (CTI)
     - Caller ID, call logs
     - Lookup (``GET /api/v1/lookup/phone/{number}``)
   * - Zammad
     - Customer support tickets
     - Planned
   * - Marketing platforms
     - Leads, campaign attribution
     - API CRUD
   * - Scheduling forms
     - Bookings, appointments
     - API CRUD
   * - Web scraping / APIs
     - Data enrichment, verification
     - API CRUD
   * - Manual entry
     - Staff input
     - API CRUD / direct SQL

.. _client-hub-api-summary:

**********************************************************************
API Endpoints
**********************************************************************

All endpoints require ``X-API-Key`` header except health check.
Base URL: ``http://10.0.1.220:8800/api/v1``

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Category
     - Endpoints
     - Purpose
   * - Health
     - ``GET /health``
     - Health check, DB connectivity
   * - Lookup
     - ``GET /lookup/phone/{number}``
       ``GET /lookup/email/{email}``
     - CTI caller ID, Chatwoot identification
   * - Contacts
     - ``GET/POST /contacts``
       ``GET/PUT/DELETE /contacts/{uuid}``
       ``POST /contacts/{uuid}/convert``
       ``GET /contacts/{uuid}/summary``
     - Full CRUD, prospect-to-client conversion,
       intelligence summary
   * - Marketing
     - ``GET/PUT /contacts/{uuid}/marketing``
     - SMS/email/phone opt-out flags (boolean 1/0)
   * - Preferences
     - ``GET /contacts/{uuid}/preferences``
       ``PUT/DELETE /contacts/{uuid}/preferences/{key}``
     - Flexible key-value preferences per contact
   * - Affiliations
     - ``GET/POST /contacts/{uuid}/affiliations``
       ``PUT/DELETE /contacts/{uuid}/affiliations/{affiliation_uuid}``
     - Multi-org junction (title, department, seniority,
       decision-maker, dates, primary). Service layer
       auto-promotes/demotes the primary so exactly one
       remains primary at all times.
   * - Organizations
     - ``GET/POST /organizations``
       ``GET/PUT/DELETE /organizations/{uuid}``
     - Company/household/practice management
   * - Orders
     - ``GET/POST /orders``
       ``GET/DELETE /orders/{uuid}``
       ``POST /orders/{uuid}/status``
     - Orders with line items, status tracking
   * - Invoices
     - ``GET/POST /invoices``
       ``GET /invoices/{uuid}``
       ``POST /invoices/{uuid}/payments``
     - Invoicing, payment recording, auto-balance
   * - Communications
     - ``GET/POST /communications``
       ``GET /communications/{uuid}``
     - Interaction log across all channels
   * - Webhooks
     - ``POST /webhooks/invoiceninja``
       ``POST /webhooks/chatwoot``
     - Inbound event processing
   * - Settings
     - ``GET/PUT /settings``
     - Business configuration
   * - Admin
     - ``GET/POST /admin/sources``
       ``GET/PUT/DELETE /admin/sources/{uuid}``
       ``GET/POST /admin/sources/{uuid}/api-keys``
       ``PUT/DELETE /admin/api-keys/{uuid}``
       ``GET /admin/events``
     - Source + API key management; cross-source event
       stream (root-key-only)
   * - Spam patterns (public)
     - ``GET /spam-patterns``
     - Source-key gated; consumer sites fetch canonical
       blocklist patterns at build time
   * - Spam admin (root-key)
     - ``GET/POST /admin/spam-patterns``
       ``PUT/DELETE /admin/spam-patterns/{uuid}``
       ``GET /admin/spam-events``
       ``GET /admin/spam-events/stats``
       ``POST /admin/spam-events/{uuid}/mark-false-positive``
     - Spam-pattern library CRUD, rejection log,
       attack analytics, false-positive correction

.. _client-hub-database-summary:

**********************************************************************
Database Schema
**********************************************************************

39 tables + 3 views in ``clienthub``, normalized to 3NF.

**Entity tables (19):** api_keys, business_settings, contacts,
organizations, contact_phones, contact_emails, contact_addresses,
org_phones, org_emails, org_addresses, contact_channel_prefs,
contact_preferences, contact_notes, orders, order_items,
order_status_history, invoices, payments, communications

**Junction tables (3):** contact_tag_map, contact_marketing_sources,
contact_org_affiliations (added migration 019; replaces the dropped
``contacts.organization_id`` cached pointer)

**Lookup tables (13):** contact_types, phone_types, email_types,
address_types, channel_types, marketing_sources, order_statuses,
order_item_types, invoice_statuses, payment_methods, tags, sources,
seniority_levels (added migration 019)

**System / observability tables (4):**

- ``_schema_migrations`` — migration tracking (added migration 018)
- ``spam_patterns`` — operator-managed spam-pattern library
  (added migration 023)
- ``spam_events`` — every rejection logged for analytics + ETL
  (added migration 023)
- ``spam_rate_log`` — sliding-window rate-limit state
  (added migration 023)

**Views (3):**

- ``v_contact_summary`` — Holistic intelligence per contact:
  lifetime value, order stats, communication stats, opt-out flags,
  marketing sources, tags, outstanding balance
- ``v_contact_last_order`` — Last order details per contact
- ``v_events_by_source`` — Cross-source event stream joining
  contacts, communications, sources, and channel types; backs the
  ``GET /api/v1/admin/events`` endpoint

Full schema documentation: ``docs/data-model.rst``

.. _client-hub-sdks:

**********************************************************************
Client SDKs
**********************************************************************

Auto-generated from the OpenAPI spec using openapi-generator-cli:

- **Python:** ``sdks/python/`` — pip-installable ``clienthub`` package
- **PHP:** ``sdks/php/`` — Composer-compatible library
- **TypeScript:** ``sdks/typescript/`` — npm-compatible, ES6

Regenerate anytime:

.. code-block:: bash

   ./scripts/generate-sdks.sh           # All SDKs
   ./scripts/generate-sdks.sh python    # Python only

.. _client-hub-testing:

**********************************************************************
Testing
**********************************************************************

Test Driven Development (TDD) — every endpoint has tests.
114 tests across 19 files, all hitting the real database.

.. code-block:: bash

   cd ~/docker/client-hub/api
   .venv/bin/python -m pytest tests/ -v           # Run all
   .venv/bin/python -m pytest tests/ -v --cov=app # With coverage

.. _client-hub-ci-cd-summary:

**********************************************************************
CI/CD
**********************************************************************

GitHub Actions pipeline (``.github/workflows/ci.yml``):

1. **Lint** — ruff (Python) + rstcheck (RST docs)
2. **Test** — pytest against MariaDB 12 service container
3. **Build** — Docker image build and verify
4. **SDK Gen** — Regenerate SDKs from OpenAPI (master only)

.. _client-hub-related-projects:

**********************************************************************
Related Projects
**********************************************************************

- ``~/docker/mariadb/`` — Shared MariaDB 12.2.2 database server
- ``~/docker/mysql-mcp-server/`` — DBHub MCP server for SQL execution

.. _client-hub-key-commands:

**********************************************************************
Key Commands
**********************************************************************

.. code-block:: bash

   # API status
   cd ~/docker/client-hub && docker compose ps

   # API logs
   docker compose logs --tail=50 client-hub-api

   # Restart API
   docker compose restart client-hub-api

   # Rebuild and restart
   docker compose down && docker compose build && docker compose up -d

   # Connect to database
   mariadb -h 10.0.1.220 -P 3306 -u root -p clienthub

   # Run tests
   cd api && .venv/bin/python -m pytest tests/ -v

   # Lint
   cd api && .venv/bin/ruff check app/ tests/

   # Generate SDKs
   ./scripts/generate-sdks.sh

   # Backup database
   docker exec mariadb mariadb-dump -u root -p clienthub > backups/dev_$(date +%Y%m%d_%H%M%S).sql

.. _client-hub-project-structure:

**********************************************************************
Project Structure
**********************************************************************

.. code-block:: text

   client-hub/
   ├── .github/workflows/ci.yml              # GitHub Actions CI pipeline
   ├── CLAUDE.md                             # Project guidance for Claude Code
   ├── README.rst                            # This file
   ├── CHANGELOG.rst                         # Chronological change log
   ├── TODO.rst                              # Task tracking
   ├── Caddyfile                             # Reverse proxy config for bundled TLS deploy
   ├── docker-compose.yml                    # Local Cybertron compose (shared mariadb)
   ├── docker-compose.bundled.yml            # Production bundled (API + MariaDB + Caddy TLS)
   ├── docker-compose.bundled-nodomain.yml   # Production bundled (no TLS)
   ├── docker-compose.override.yml.example   # Local override example (cross-DB access)
   ├── docker-compose.opsinsights.yml        # Per-VPS OpsInsights override (gitignored;
   │                                         #  written by setup-opsinsights-tls.sh)
   ├── .env                                  # Environment variables (git-ignored)
   ├── .env.example                          # Template for .env
   ├── .gitignore
   ├── api/                                  # FastAPI application
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   ├── ruff.toml
   │   ├── pytest.ini
   │   ├── app/                              # Application code
   │   │   ├── main.py
   │   │   ├── config.py
   │   │   ├── database.py
   │   │   ├── models/                       # SQLAlchemy ORM models
   │   │   ├── schemas/                      # Pydantic request/response
   │   │   ├── routers/                      # Endpoint handlers (12 routers)
   │   │   ├── services/                     # Business logic
   │   │   └── middleware/                   # API key auth (root + source-scoped)
   │   └── tests/                            # 114 tests, 19 files
   ├── migrations/                           # 22 numbered SQL files (001-023)
   │   └── dev/                              # Dev/CI-only seed data
   │       └── 012_seed_test_data.sql
   ├── scripts/                              # 12 shell scripts
   │   ├── install.sh                        # One-line production installer
   │   ├── uninstall.sh                      # Preserves .env + install summary
   │   ├── upgrade.sh                        # Coordinated VPS upgrade runner
   │   ├── bootstrap-migrations.sh           # Migration runner (--via-docker for bundled VPSes)
   │   ├── backfill-schema-tracker.sh        # Record pre-mig-018 migrations as applied
   │   ├── detect-drift.sh                   # Sanity-check FK column types pre-upgrade
   │   ├── setup-opsinsights-tls.sh          # OpsInsights TLS + IP-allowlist setup
   │   ├── generate-sdks.sh                  # SDK generation (Python/PHP/TS)
   │   ├── generate-api-key.sh               # Create source-scoped API keys
   │   ├── smoke-test.sh                     # Post-install smoke test
   │   ├── cleanup-test-data.sh              # Strip seed data from contaminated prod
   │   └── backup.sh                         # Database backup helper
   ├── sdks/                                 # Auto-generated client SDKs
   │   ├── openapi.json                      # Cached OpenAPI spec
   │   ├── python/
   │   ├── php/
   │   └── typescript/
   ├── docs/                                 # RST documentation (18 files)
   │   ├── architecture.rst
   │   ├── data-model.rst
   │   ├── api-design.rst
   │   ├── ci-cd.rst
   │   ├── Migration-Strategy.rst
   │   ├── Spam-Defense-Pattern.rst
   │   ├── Multi-Source.rst
   │   ├── Deployment.rst
   │   ├── Upgrade.rst
   │   ├── Data-Privacy.rst
   │   ├── Cross-Project-Integration.rst
   │   ├── OpsInsights-Direct-TLS-Plan.rst
   │   ├── OpsInsights-Setup-Prompt.rst
   │   ├── OpsInsights-SSH-Tunnel-Plan.rst
   │   ├── Installation-Implementation-Prompt.rst
   │   ├── Post-Deployment-Fixes-Prompt.rst
   │   ├── External-Refs-Json-Fix-Prompt.rst
   │   └── Dental-Care-Payload-Fix-Prompt.rst
   └── upgrades/                             # Pre-upgrade analysis docs

.. _client-hub-references:

**********************************************************************
References
**********************************************************************

- `GitHub Repository <https://github.com/stancel/client-hub>`_
- `FastAPI Documentation <https://fastapi.tiangolo.com/>`_
- `SQLAlchemy Async <https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html>`_
- `MariaDB Docker Hub <https://hub.docker.com/_/mariadb>`_
- `MariaDB Documentation <https://mariadb.com/kb/en/documentation/>`_
- `OpenAPI Generator <https://openapi-generator.tech/>`_
