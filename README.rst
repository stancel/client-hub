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
     - ``dev_schema`` (development)
   * - **Schema**
     - 31 tables + 2 views (3NF normalized)
   * - **API Endpoints**
     - 23 paths across 9 routers
   * - **Test Suite**
     - 63 tests across 13 files
   * - **SDKs**
     - Python, PHP, TypeScript (auto-generated from OpenAPI)
   * - **CI/CD**
     - GitHub Actions (lint → test → build → SDK gen)
   * - **MCP Tools**
     - ``apisix-mysql`` (``execute_sql``, ``search_objects``)
   * - **Status**
     - All phases complete. Ready for live integrations.

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
   │    23 endpoints, API key auth          │
   │    Swagger UI at /docs                 │
   └─────────────────┬───────────────────────┘
                     │ SQLAlchemy (async)
                     ▼
   ┌─────────────────────────────────────────┐
   │     Shared MariaDB 12.2.2              │
   │     ~/docker/mariadb/ (port 3306)      │
   │     Database: dev_schema               │
   │     31 tables + 2 views (3NF)          │
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

.. _client-hub-database-summary:

**********************************************************************
Database Schema
**********************************************************************

31 tables + 2 views in ``dev_schema``, normalized to 3NF.

**Entity tables (18):** business_settings, contacts, organizations,
contact_phones, contact_emails, contact_addresses, org_phones,
org_emails, org_addresses, contact_channel_prefs,
contact_preferences, contact_notes, orders, order_items,
order_status_history, invoices, payments, communications

**Junction tables (2):** contact_tag_map, contact_marketing_sources

**Lookup tables (11):** contact_types, phone_types, email_types,
address_types, channel_types, marketing_sources, order_statuses,
order_item_types, invoice_statuses, payment_methods, tags

**Views (2):**

- ``v_contact_summary`` — Holistic intelligence per contact:
  lifetime value, order stats, communication stats, opt-out flags,
  marketing sources, tags, outstanding balance
- ``v_contact_last_order`` — Last order details per contact

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
63 tests across 13 files, all hitting the real database.

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
   mariadb -h 10.0.1.220 -P 3306 -u root -p dev_schema

   # Run tests
   cd api && .venv/bin/python -m pytest tests/ -v

   # Lint
   cd api && .venv/bin/ruff check app/ tests/

   # Generate SDKs
   ./scripts/generate-sdks.sh

   # Backup database
   docker exec mariadb mariadb-dump -u root -p dev_schema > backups/dev_$(date +%Y%m%d_%H%M%S).sql

.. _client-hub-project-structure:

**********************************************************************
Project Structure
**********************************************************************

.. code-block:: text

   client-hub/
   ├── .github/workflows/ci.yml  # GitHub Actions CI pipeline
   ├── CLAUDE.md                 # Project guidance for Claude Code
   ├── README.rst                # This file
   ├── CHANGELOG.rst             # Chronological change log
   ├── TODO.rst                  # Task tracking
   ├── docker-compose.yml        # API container on my-main-net
   ├── .env                      # Environment variables (git-ignored)
   ├── .env.example              # Template for .env
   ├── .gitignore
   ├── api/                      # FastAPI application
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   ├── ruff.toml
   │   ├── pytest.ini
   │   ├── app/                  # Application code
   │   │   ├── main.py
   │   │   ├── config.py
   │   │   ├── database.py
   │   │   ├── models/           # SQLAlchemy ORM models
   │   │   ├── schemas/          # Pydantic request/response
   │   │   ├── routers/          # Endpoint handlers
   │   │   ├── services/         # Business logic
   │   │   └── middleware/       # Auth
   │   └── tests/                # 63 tests, 13 files
   ├── migrations/               # 13 numbered SQL files
   ├── scripts/
   │   └── generate-sdks.sh      # SDK generation script
   ├── sdks/                     # Auto-generated client SDKs
   │   ├── python/
   │   ├── php/
   │   └── typescript/
   ├── docs/                     # RST documentation
   │   ├── architecture.rst
   │   ├── data-model.rst
   │   ├── api-design.rst
   │   └── ci-cd.rst
   └── upgrades/                 # Pre-upgrade analysis docs

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
