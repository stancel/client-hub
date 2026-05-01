.. _client-hub-architecture:

######################################################################
Client Hub — Architecture
######################################################################

.. _client-hub-arch-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub is a **data-first customer intelligence microservice**
built on MariaDB that provides a single source of truth for client
and prospect information across multiple business verticals.

This is a data-first system: the database schema is the primary
product. External applications can integrate at two levels:

1. **API level** — REST endpoints via the FastAPI container
2. **Database level** — Direct SQL from containers on ``my-main-net``
   or via MCP tools (``apisix-mysql``)

Both patterns are valid and supported.

.. _client-hub-arch-infrastructure:

**********************************************************************
Infrastructure Dependencies
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Project
     - Location
     - Role
   * - MariaDB
     - ``~/docker/mariadb/``
     - Shared database server (MariaDB 12.2.2, port 3306)
   * - MySQL MCP Server
     - ``~/docker/mysql-mcp-server/``
     - DBHub MCP tools (``execute_sql``, ``search_objects``)

.. _client-hub-arch-containers:

**********************************************************************
Container Layout
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 25 25 15 15 20

   * - Container
     - Image
     - Host Port
     - Container Port
     - Purpose
   * - client-hub-api
     - client-hub-client-hub-api
     - 8800
     - 8800
     - FastAPI REST API (Python 3.12)

.. _client-hub-arch-network:

**********************************************************************
Network Architecture
**********************************************************************

All containers run on the ``my-main-net`` Docker bridge network.
The API container connects to the shared MariaDB instance via
Docker DNS (``mariadb:3306``).

.. code-block:: text

   External Systems (Chatwoot, InvoiceNinja, CTI, etc.)
          │
          ▼ HTTP (webhooks, REST, lookups)
   ┌─────────────────────────────────────────┐
   │    client-hub-api (FastAPI)             │
   │    Port 8800 on my-main-net            │
   │    37 endpoints, X-API-Key auth        │
   │    Swagger: /docs  OpenAPI: /openapi.json│
   └─────────────────┬───────────────────────┘
                     │ SQLAlchemy async (aiomysql)
                     ▼
   ┌─────────────────────────────────────────┐
   │    Shared MariaDB 12.2.2               │
   │    ~/docker/mariadb/ (port 3306)       │
   │    Database: clienthub                │
   │    39 tables + 3 views (3NF)           │
   └─────────────────────────────────────────┘
          ▲                    ▲
          │                    │
   Direct SQL from         MCP tools via
   my-main-net containers  mysql-mcp-server

.. _client-hub-arch-database:

**********************************************************************
Database Configuration
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Setting
     - Value
   * - Database name
     - ``clienthub``
   * - Docker DNS host
     - ``mariadb``
   * - Port
     - ``3306``
   * - Host access
     - ``10.0.1.220:3306``
   * - Tables
     - 39 (19 entity + 1 identity/auth + 3 junction + 12 lookup +
       3 spam-defense + 1 system). See ``docs/data-model.rst`` for
       the full breakdown.
   * - Views
     - 3 (``v_contact_summary``, ``v_contact_last_order``,
       ``v_events_by_source``)
   * - Migrations
     - 28 files in ``migrations/`` (numbered 001-029, with 012 in
       ``migrations/dev/`` as CI/dev seed data)

.. _client-hub-arch-env:

**********************************************************************
Environment Configuration
**********************************************************************

Environment variables stored in ``.env`` (git-ignored), templated
in ``.env.example`` (committed).

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Variable
     - Required
     - Description
   * - ``DB_NAME``
     - No
     - Database name (default: ``clienthub``)
   * - ``DB_USER``
     - No
     - Database user (default: ``root``)
   * - ``DB_PASSWORD``
     - Yes
     - Database password
   * - ``API_KEY``
     - No
     - API authentication key (default: ``dev-api-key``)

.. _client-hub-arch-api:

**********************************************************************
API Architecture
**********************************************************************

Stack: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), aiomysql,
Pydantic v2.

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Layer
     - Directory
     - Purpose
   * - Routers
     - ``api/app/routers/``
     - Endpoint handlers (13 router modules including
       ``marketing_sources.py`` and ``spam.py``)
   * - Services
     - ``api/app/services/``
     - Business logic (contact, lookup, webhook, phone_utils,
       request_meta, marketing_source_service,
       spam_filter_service, etc.)
   * - Models
     - ``api/app/models/``
     - SQLAlchemy ORM (~10 model modules)
   * - Schemas
     - ``api/app/schemas/``
     - Pydantic request/response validation (the
       ``ContactCreatePhone.number`` validator coerces inbound
       phones to E.164 — see ``docs/data-model.rst``)
   * - Middleware
     - ``api/app/middleware/``
     - API key authentication; resolves ``X-API-Key`` →
       ``api_keys`` row → parent ``sources`` row → stamps
       ``ctx.source_id`` onto every authenticated write
   * - Tests
     - ``api/tests/``
     - 180 tests across 22 files (TDD, real DB)

.. _client-hub-arch-data-model:

**********************************************************************
Data Model Design Principles
**********************************************************************

1. **Data-first** — Schema is the product. DDL before API.

2. **Business-agnostic** — No industry-specific columns. Business
   context via configurable lookup tables and key-value preferences.

3. **Third Normal Form (3NF)** — Fully normalized with no transitive
   dependencies.

4. **Single-tenant** — One database per business deployment.

5. **Audit trail** — All tables include ``created_at``,
   ``updated_at``, and ``created_by`` columns.

6. **Soft deletes** — ``is_active`` / ``deleted_at`` rather than
   hard deletes.

7. **Referential integrity** — Foreign keys enforced at the database
   level with appropriate cascade rules.

8. **Data provenance** — Contact details track source, enrichment
   status, and verification timestamps.

9. **Explicit marketing flags** — Boolean 1/0 opt-out columns for
   SMS, email, and phone on the contacts table.

.. _client-hub-arch-integrations:

**********************************************************************
Integration Architecture
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 20 15 25 40

   * - System
     - Direction
     - Mechanism
     - Status
   * - Chatwoot
     - Bidirectional
     - Webhook + lookup
     - Endpoint ready, live integration pending
   * - InvoiceNinja
     - Inbound
     - Webhook
     - Endpoint ready, live integration pending
   * - CTI (SIP/Phone)
     - Outbound query
     - Phone lookup API
     - Endpoint ready, live integration pending
   * - Zammad
     - Bidirectional
     - API CRUD
     - Planned
   * - Marketing platforms
     - Inbound
     - API CRUD
     - Planned
   * - Scheduling forms
     - Inbound
     - API CRUD
     - Planned
   * - Web scraping
     - Inbound
     - API CRUD
     - Planned

.. _client-hub-arch-sdks:

**********************************************************************
Client SDKs
**********************************************************************

Auto-generated from the OpenAPI spec at ``/openapi.json`` using
``openapi-generator-cli`` v7.12.0 (Docker-based).

- **Python** — ``sdks/python/`` — pip-installable ``clienthub``
- **PHP** — ``sdks/php/`` — Composer-compatible
- **TypeScript** — ``sdks/typescript/`` — npm-compatible, ES6

Regenerate: ``./scripts/generate-sdks.sh``

.. _client-hub-arch-ci-cd:

**********************************************************************
CI/CD Pipeline
**********************************************************************

GitHub Actions (``.github/workflows/ci.yml``):

1. **Lint** — ruff (Python) + rstcheck (RST docs)
2. **Test** — pytest against MariaDB 12 service container
3. **Build** — Docker image build and verify
4. **SDK Gen** — Regenerate SDKs (master branch only)

See ``docs/ci-cd.rst`` for full details.
