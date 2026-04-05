.. _client-hub-readme:

######################################################################
Client Hub
######################################################################

.. _client-hub-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub is a centralized, business-agnostic MariaDB database that
serves as a single source of truth for client data, prospect data,
orders and bookings, marketing channel preferences, and communication
history. External programs integrate through a wrapper REST API layer.

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
   * - **MariaDB Port**
     - ``3307`` (host) → ``3306`` (container)
   * - **API Port**
     - ``8800`` (planned — Phase 2)
   * - **Local URL**
     - http://10.0.1.220:8800 (not yet active)
   * - **Public URL**
     - None (planned for Phase 4)
   * - **Database**
     - MariaDB 11
   * - **Status**
     - Phase 1 — Data model design

.. _client-hub-architecture-summary:

**********************************************************************
Architecture
**********************************************************************

Phase 1 (current) deploys a single MariaDB container. Phase 2 will
add a containerized REST API service.

.. code-block:: text

   ┌─────────────────────────────────┐
   │         client-hub-db           │
   │   MariaDB 11 (port 3307)       │
   │   Database: clienthub_db       │
   └─────────────────────────────────┘
              ▲
              │ (Phase 2)
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

.. _client-hub-key-commands:

**********************************************************************
Key Commands
**********************************************************************

.. code-block:: bash

   # Start
   cd ~/docker/client-hub && docker compose up -d

   # Status
   docker compose ps

   # Logs
   docker compose logs --tail=50

   # Connect to MariaDB
   docker compose exec client-hub-db mariadb -u clienthub -p clienthub_db

   # Stop
   docker compose down

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
- `MariaDB 11 Release Notes <https://mariadb.com/kb/en/release-notes-mariadb-11-series/>`_
