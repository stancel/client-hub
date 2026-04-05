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

.. _client-hub-arch-containers:

**********************************************************************
Container Layout
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Container
     - Image
     - Host Port
     - Container Port
     - Purpose
   * - client-hub-db
     - mariadb:11
     - 3307
     - 3306
     - MariaDB database
   * - client-hub-api
     - TBD
     - 8800
     - 8800
     - REST API wrapper (Phase 2)

.. _client-hub-arch-ports:

**********************************************************************
Port Mappings
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 40

   * - Service
     - Host Port
     - Container Port
     - Notes
   * - MariaDB
     - 3307
     - 3306
     - Port 3306 already in use by another service
   * - REST API
     - 8800
     - 8800
     - Planned for Phase 2

.. _client-hub-arch-volumes:

**********************************************************************
Data Volumes
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Volume
     - Host Path
     - Purpose
   * - db-data
     - ``./data/mariadb/``
     - MariaDB data directory (git-ignored)
   * - db-init
     - ``./init/``
     - SQL initialization scripts (committed)
   * - db-backups
     - ``./backups/``
     - Database backup files (git-ignored)

.. _client-hub-arch-network:

**********************************************************************
Network Architecture
**********************************************************************

All containers run on the ``client-hub-net`` Docker bridge network.
The MariaDB port (3307) is exposed to the host for direct access
during development. In production, only the API container port (8800)
should be exposed externally.

.. code-block:: text

   Host Network (10.0.1.220)
   │
   ├── :3307 ──► client-hub-db (MariaDB)
   │                    ▲
   │                    │ internal network
   │                    │ (client-hub-net)
   └── :8800 ──► client-hub-api (REST API)

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
   * - ``MARIADB_ROOT_PASSWORD``
     - Yes
     - Root password for MariaDB
   * - ``MARIADB_DATABASE``
     - No
     - Database name (default: ``clienthub_db``)
   * - ``MARIADB_USER``
     - No
     - Application user (default: ``clienthub``)
   * - ``MARIADB_PASSWORD``
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
