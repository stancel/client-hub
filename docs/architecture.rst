.. _client-hub-architecture:

######################################################################
Client Hub — Architecture
######################################################################

.. _client-hub-arch-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub is a centralized data platform built on MariaDB that
provides a single source of truth for client and prospect information
across multiple business verticals. External applications interact
exclusively through a REST API wrapper layer — no direct database
access is permitted from external systems.

Client Hub does **not** run its own database. It uses the shared
MariaDB instance at ``~/docker/mariadb/`` and the MySQL MCP Server
at ``~/docker/mysql-mcp-server/`` for schema design.

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

Phase 1 (current): No containers — schema design only.

Phase 2 (planned):

.. list-table::
   :header-rows: 1
   :widths: 25 20 15 15 25

   * - Container
     - Image
     - Host Port
     - Container Port
     - Purpose
   * - client-hub-api
     - TBD
     - 8800
     - 8800
     - REST API wrapper

.. _client-hub-arch-network:

**********************************************************************
Network Architecture
**********************************************************************

The API container (Phase 2) will join ``my-main-net`` to reach the
shared MariaDB instance via Docker DNS (``mariadb:3306``).

.. code-block:: text

   Shared Network: my-main-net
   │
   ├── mariadb:3306 (~/docker/mariadb/)
   │       ▲
   │       │ SQL queries
   │       │
   ├── client-hub-api:8800 (Phase 2)
   │       ▲
   │       │ REST / Webhooks
   │
   └── mysql-mcp-server:8080 (~/docker/mysql-mcp-server/)
           ▲
           │ MCP tools (schema design)

Host access: ``10.0.1.220:3306`` for direct MariaDB connections.

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
     - ``clienthub_db``
   * - Application user
     - ``clienthub``
   * - Docker DNS host
     - ``mariadb``
   * - Port
     - ``3306``
   * - Host access
     - ``10.0.1.220:3306``

.. _client-hub-arch-env:

**********************************************************************
Environment Configuration
**********************************************************************

Environment variables are stored in ``.env`` (git-ignored) and
templated in ``.env.example`` (committed).

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Variable
     - Required
     - Description
   * - ``DB_USER``
     - No
     - Application user (default: ``clienthub``)
   * - ``DB_PASSWORD``
     - Yes
     - Application user password

.. _client-hub-arch-data-model:

**********************************************************************
Data Model Design Principles
**********************************************************************

The database schema follows these principles:

1. **Business-agnostic** — No industry-specific columns. Business
   context is stored as configurable metadata using lookup tables
   and key-value patterns where appropriate.

2. **Third Normal Form (3NF)** — Fully normalized with no transitive
   dependencies. Denormalization only at the API/view layer if needed
   for performance.

3. **Multi-tenant** — Every record is scoped to a business/tenant.
   Row-level isolation from day one.

4. **Audit trail** — All tables include ``created_at``,
   ``updated_at``, and ``created_by`` columns.

5. **Soft deletes** — Records use ``is_active`` / ``deleted_at``
   rather than hard deletes.

6. **Referential integrity** — Foreign keys enforced at the database
   level with appropriate cascade rules.

.. _client-hub-arch-core-entities:

Core Entities (Planned)
----------------------------------------------------------------------

- **businesses** — Tenant/business records
- **contacts** — Clients and prospects
- **contact_types** — Client, prospect, lead, vendor, etc.
- **addresses** — Polymorphic address records
- **channels** — Communication channel definitions
- **contact_channels** — Contact preferences per channel
- **orders** — Orders and bookings
- **order_items** — Line items within orders
- **communications** — Communication log entries
- **notes** — Free-text notes attached to any entity

.. _client-hub-arch-integrations:

**********************************************************************
Integration Architecture
**********************************************************************

External systems interact with Client Hub exclusively through the
REST API. The API provides:

- **CRUD endpoints** for all core entities
- **Webhook receivers** for inbound events (e.g., InvoiceNinja
  payment notifications)
- **Search/lookup endpoints** for CTI caller identification
- **Bulk operations** for data import/export

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 40

   * - System
     - Direction
     - Mechanism
     - Use Case
   * - Chatwoot
     - Bidirectional
     - REST webhooks
     - Sync customer data on chat events
   * - InvoiceNinja
     - Inbound
     - REST webhooks
     - Payment and contact update events
   * - CTI
     - Outbound query
     - REST GET
     - Caller ID lookup on incoming calls
   * - Website Chatbot
     - Via Chatwoot
     - REST
     - Customer queries routed through Chatwoot
