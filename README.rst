.. _client-hub-readme:

######################################################################
Client Hub
######################################################################

.. _client-hub-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub is a centralized, business-agnostic database that serves as
a single source of truth for client data, prospect data, orders and
bookings, marketing channel preferences, and communication history.
External programs integrate through a wrapper REST API layer.

**Initial use case:** Embroidery business CRM. **Future verticals:**
Dentist offices, lawn care, pressure washing, and other service
businesses.

.. _client-hub-quick-info:

**********************************************************************
Quick Info
**********************************************************************

.. list-table::
   :widths: 30 70

   * - **App Location**
     - ``~/docker/client-hub/``
   * - **Database**
     - Shared MariaDB 12.2.2 at ``~/docker/mariadb/``
   * - **DB Host**
     - ``mariadb:3306`` (Docker DNS) / ``10.0.1.220:3306`` (host)
   * - **DB Name**
     - ``clienthub_db``
   * - **API Port**
     - ``8800`` (planned — Phase 2)
   * - **Public URL**
     - None (planned for Phase 4)
   * - **MCP Tools**
     - ``apisix-mysql`` (``execute_sql``, ``search_objects``)
   * - **Status**
     - Phase 1 — Data model design

.. _client-hub-architecture-summary:

**********************************************************************
Architecture
**********************************************************************

Client Hub uses the shared MariaDB instance at ``~/docker/mariadb/``
rather than running its own database container. Schema design is done
through the MySQL MCP Server (DBHub) at ``~/docker/mysql-mcp-server/``.
Phase 2 will add a containerized REST API service.

.. code-block:: text

   ┌─────────────────────────────────┐
   │  Shared MariaDB 12.2.2         │
   │  ~/docker/mariadb/             │
   │  Database: clienthub_db        │
   │  Port: 3306                    │
   └─────────────────────────────────┘
              ▲
              │ my-main-net (Phase 2)
   ┌─────────────────────────────────┐
   │        client-hub-api           │
   │   REST API (port 8800)         │
   └─────────────────────────────────┘
              ▲
              │ Webhooks / REST
   ┌──────┬──────┬──────┬───────────┐
   │Chatwoot│Invoice│ CTI │ Chatbot  │
   │       │ Ninja │     │          │
   └──────┴──────┴──────┴───────────┘

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

   # Connect to MariaDB (from host)
   mariadb -h 10.0.1.220 -P 3306 -u clienthub -p clienthub_db

   # Connect via container
   docker exec -it mariadb mariadb -u clienthub -p clienthub_db

   # Backup
   docker exec mariadb mariadb-dump -u root -p clienthub_db > backups/clienthub_$(date +%Y%m%d_%H%M%S).sql

   # Check shared MariaDB status
   cd ~/docker/mariadb && docker compose ps

.. _client-hub-integration-targets:

**********************************************************************
Integration Targets
**********************************************************************

- **Chatwoot** — Bidirectional sync of customer data via REST webhooks
- **InvoiceNinja** — Payment and contact update events pushed to hub
- **CTI (Computer Telephony Integration)** — Caller ID lookup via API
- **Website Chatbot** — Customer queries routed through Chatwoot

.. _client-hub-references:

**********************************************************************
References
**********************************************************************

- `MariaDB Docker Hub <https://hub.docker.com/_/mariadb>`_
- `MariaDB Documentation <https://mariadb.com/kb/en/documentation/>`_
- `MariaDB 12 Release Notes <https://mariadb.com/kb/en/release-notes-mariadb-12-series/>`_
