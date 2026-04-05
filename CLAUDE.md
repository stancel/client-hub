# CLAUDE.md — client-hub

## Project Overview

**Client Hub** is a **data-first customer intelligence microservice** — a centralized, business-agnostic MariaDB data store that compiles and enriches information from disparate systems (invoicing, marketing, telephony, chat, support, scheduling, web scraping) into a single source of truth. The database schema is the primary product; the REST API is a convenience layer. Both DB-level and API-level integration are valid patterns.

- **App location:** `~/docker/client-hub/`
- **Local URL:** http://10.0.1.220:8800 (API — not yet active)
- **Public URL:** None (will be exposed after API layer is complete)
- **Current status:** Phase 4 — API design (schema complete in dev_schema)
- **Schema:** 31 tables + 2 views in `dev_schema`

### Data Sources That Feed Into Client Hub

| System | What It Provides |
|---|---|
| InvoiceNinja | Invoicing, payments, contact updates |
| Chatwoot | SMS/MMS, web chat, messaging |
| SIP/Phone (CTI) | Call logs, caller ID |
| Zammad | Support tickets, interactions |
| Marketing platforms | Leads, campaign attribution |
| Scheduling forms | Bookings, appointments |
| Web scraping / APIs | Data enrichment, verification |
| Manual entry | Staff input |

## Database Infrastructure

Client Hub does **not** run its own database container. It uses the shared MariaDB instance:

| Detail | Value |
|---|---|
| MariaDB project | `~/docker/mariadb/` |
| MariaDB version | 12.2.2 |
| Docker DNS | `mariadb:3306` (via `my-main-net`) |
| Host access | `10.0.1.220:3306` |
| Database name | `dev_schema` (development) |
| MCP tools | `apisix-mysql` (`execute_sql`, `search_objects`) via `~/docker/mysql-mcp-server/` |

### Schema Design Workflow

Use the **mysql-mcp-server** (DBHub) MCP tools for all schema work:
- `execute_sql` — Run DDL/DML queries with transaction support
- `search_objects` — Inspect schemas, tables, columns, indexes

These are available as the `apisix-mysql` MCP server in Claude Code.

## Architecture

### Current (Phase 1)

No containers — schema design only, using the shared MariaDB and MCP tools.

### Planned (Phase 2+)

| Container | Image | Port (host:container) | Purpose |
|---|---|---|---|
| client-hub-api | TBD | 8800:8800 | REST API wrapper |

The API container will join `my-main-net` to reach `mariadb:3306`.

### Key Directories

```
client-hub/
├── init/             # SQL schema and seed scripts
├── api/              # API source code (Phase 2)
├── docs/             # RST documentation
├── upgrades/         # Pre-upgrade analysis documents
└── screenshots/      # Local-only reference (git-ignored)
```

## Compose Files

- `docker-compose.yml` — Will hold the API service (Phase 2); currently a placeholder

## Integration Points

| System | Direction | Mechanism | Status |
|---|---|---|---|
| Chatwoot | Bidirectional | REST API webhooks | Planned |
| InvoiceNinja | Inbound | REST API webhooks | Planned |
| CTI (Telephony) | Outbound query | REST API GET | Planned |
| Website Chatbot | Via Chatwoot | REST API | Planned |

## Key Commands

```bash
# Connect to MariaDB (from host)
mariadb -h 10.0.1.220 -P 3306 -u clienthub -p clienthub_db

# Connect via shared MariaDB container
docker exec -it mariadb mariadb -u clienthub -p clienthub_db

# Backup database
docker exec mariadb mariadb-dump -u root -p"$MARIADB_ROOT_PASSWORD" clienthub_db > backups/clienthub_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker exec -i mariadb mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub_db < backups/FILENAME.sql

# Check shared MariaDB status
cd ~/docker/mariadb && docker compose ps
```

## Troubleshooting

```bash
# Check shared MariaDB is running
cd ~/docker/mariadb && docker compose ps

# View MariaDB logs
cd ~/docker/mariadb && docker compose logs --tail=50

# Test database connectivity
mariadb -h 10.0.1.220 -P 3306 -u clienthub -p -e "SELECT 1;"

# Check if clienthub_db exists
docker exec mariadb mariadb -u root -p -e "SHOW DATABASES;"

# Check MCP server is available
cd ~/docker/mysql-mcp-server && docker compose ps

# Check disk usage
docker system df -v 2>&1 | grep mariadb
```

## Data Model Design Principles

- **Data-first:** The schema is the product. Design DDL first, API second.
- **Business-agnostic:** No business-specific columns; use configurable metadata patterns
- **Third Normal Form (3NF):** Fully normalized, no transitive dependencies
- **Single-tenant:** One database per business — NOT multi-tenant in a single DB
- **Audit trail:** Track all changes with created_at/updated_at/created_by
- **Soft deletes:** Use is_active/deleted_at rather than hard deletes
- **Data provenance:** Track enriched vs. manually entered fields, source, last verified
- **Explicit opt-out flags:** Boolean 1/0 for marketing opt-outs (SMS, email, phone)
- **DB-level intelligence:** Views (`v_contact_summary`, `v_contact_last_order`) available via SQL

## Key Database Views

- `v_contact_summary` — Holistic intelligence: lifetime value, order stats, communication stats, marketing sources, tags, opt-outs, outstanding balance
- `v_contact_last_order` — Last order details per contact: order number, date, status, total, item types
