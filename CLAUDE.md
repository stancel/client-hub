# CLAUDE.md — client-hub

## Project Overview

**Client Hub** is a **data-first customer intelligence microservice** — a centralized, business-agnostic MariaDB data store that compiles and enriches information from disparate systems (invoicing, marketing, telephony, chat, support, scheduling, web scraping) into a single source of truth. The database schema is the primary product; the REST API is a convenience layer. Both DB-level and API-level integration are valid patterns.

- **App location:** `~/docker/client-hub/`
- **API URL:** http://10.0.1.220:8800
- **Swagger UI:** http://10.0.1.220:8800/docs
- **OpenAPI Spec:** http://10.0.1.220:8800/openapi.json
- **Public URL:** None (will be exposed after live integrations are proven)
- **GitHub:** https://github.com/stancel/client-hub
- **Schema:** 34 tables + 3 views in `dev_schema` (3NF)
- **API:** 28 endpoint paths, 89 tests passing
- **SDKs:** Python, PHP, TypeScript (auto-generated)
- **CI/CD:** GitHub Actions (lint → test → build → SDK gen)
- **Deployment:** one-line installer (`scripts/install.sh`); first
  production VPS running at
  `client-hub-complete-dental-care.onlinesalessystems.com`

### Data Sources That Feed Into Client Hub

| System | What It Provides | Integration Method |
|---|---|---|
| InvoiceNinja | Invoicing, payments, contact updates | Webhook endpoint |
| Chatwoot | SMS/MMS, web chat, messaging | Webhook endpoint |
| SIP/Phone (CTI) | Call logs, caller ID | Phone lookup endpoint |
| Zammad | Support tickets, interactions | Planned |
| Marketing platforms | Leads, campaign attribution | API CRUD |
| Scheduling forms | Bookings, appointments | API CRUD |
| Web scraping / APIs | Data enrichment, verification | API CRUD |
| Manual entry | Staff input | API CRUD / direct SQL |

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

### Containers

| Container | Image | Port (host:container) | Purpose |
|---|---|---|---|
| client-hub-api | client-hub-client-hub-api (local build) | 8800:8800 | FastAPI REST API |

The API container runs on `my-main-net` and connects to `mariadb:3306`.

### Key Directories

```
client-hub/
├── api/                                  # FastAPI application (Python 3.12)
│   ├── app/                              # Models, routers, schemas, services, middleware
│   └── tests/                            # 89 tests across 17 files
├── migrations/                           # 17 numbered SQL migrations (001-018, 012 in dev/)
│   └── dev/                              # Dev/CI-only seed data (012_seed_test_data.sql)
├── scripts/                              # install.sh, uninstall.sh, bootstrap-migrations.sh,
│                                         # generate-sdks.sh, smoke-test.sh, cleanup-test-data.sh,
│                                         # generate-api-key.sh, backup.sh
├── sdks/                                 # Auto-generated Python, PHP, TypeScript SDKs
├── docs/                                 # RST documentation (13 files) + handoff prompts
├── upgrades/                             # Pre-upgrade analysis documents
├── .github/                              # CI/CD workflows
├── docker-compose.yml                    # Local Cybertron compose (my-main-net, shared mariadb)
├── docker-compose.bundled.yml            # Production bundled (API + MariaDB + Caddy with TLS)
├── docker-compose.bundled-nodomain.yml   # Production bundled (no TLS)
└── docker-compose.override.yml.example   # OpsInsights cross-DB access example
```

## API Endpoints (28 paths)

| Category | Endpoints |
|---|---|
| Health | `GET /api/v1/health` |
| Lookup | `GET /api/v1/lookup/phone/{number}`, `GET /api/v1/lookup/email/{email}` |
| Contacts | CRUD + convert + summary + marketing opt-outs + preferences |
| Organizations | CRUD |
| Orders | CRUD + status changes with history |
| Invoices | CRUD + payment recording (auto-balance update) |
| Communications | List, get, create interaction logs |
| Webhooks | `POST /api/v1/webhooks/invoiceninja`, `POST /api/v1/webhooks/chatwoot` |
| Settings | `GET/PUT /api/v1/settings` |
| Admin | `GET/POST /api/v1/admin/sources`, `GET/PUT/DELETE /api/v1/admin/sources/{uuid}`, source-scoped API key CRUD, `GET /api/v1/admin/events` (root-key-only) |

Auth: `X-API-Key` header on all protected routes. Multi-source
model: one root key plus per-source scoped keys. Source attribution
is auto-stamped on contacts and communications via
`first_seen_source_id`.

Contact/Organization/Order create/update accept a free-form
`external_refs_json: dict[str, Any]` field for integration
metadata (scheduler payloads, Eaglesoft IDs, request headers,
UTM parameters). See `docs/Cross-Project-Integration.rst` for the
canonical payload contract.

## Key Commands

```bash
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

# Lint Python
cd api && .venv/bin/ruff check app/ tests/

# Generate SDKs
./scripts/generate-sdks.sh

# Backup database
docker exec mariadb mariadb-dump -u root -p dev_schema > backups/dev_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker exec -i mariadb mariadb -u root -p dev_schema < backups/FILENAME.sql

# Provision a new production VPS (one-line installer)
curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh | sudo bash

# Smoke test (post-deploy)
./scripts/smoke-test.sh
```

## Troubleshooting

```bash
# Check API container
docker compose ps
docker compose logs --tail=50 client-hub-api

# Check shared MariaDB is running
cd ~/docker/mariadb && docker compose ps

# Test database connectivity
mariadb -h 10.0.1.220 -P 3306 -u root -p -e "USE dev_schema; SELECT COUNT(*) FROM contacts;"

# Test API health
curl -s http://10.0.1.220:8800/api/v1/health | python3 -m json.tool

# Test authenticated endpoint
curl -s -H "X-API-Key: dev-api-key" http://10.0.1.220:8800/api/v1/contacts | python3 -m json.tool

# Check MCP server is available
cd ~/docker/mysql-mcp-server && docker compose ps

# Check disk usage
docker system df -v 2>&1 | grep -E "mariadb|client-hub"

# Full recreate
docker compose down && docker compose build --no-cache && docker compose up -d
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
- `v_events_by_source` — Cross-source event stream for the admin events endpoint, joining contacts/communications/sources with channel and source filters

## Testing (TDD)

Every API endpoint has a corresponding test. Tests hit the real database.

- **89 tests** across 17 test files
- Framework: pytest + httpx + AsyncClient
- Run: `cd api && .venv/bin/python -m pytest tests/ -v`
- Coverage: `pytest --cov=app --cov-report=term-missing`

## SDK Generation

Auto-generated from OpenAPI spec. Regenerate on any API change:

```bash
./scripts/generate-sdks.sh           # All: Python, PHP, TypeScript
./scripts/generate-sdks.sh python    # Just Python
```

## CI/CD Pipeline

GitHub Actions (`.github/workflows/ci.yml`):
1. **Lint** — ruff + rstcheck
2. **Test** — pytest against MariaDB 12 service container
3. **Build** — Docker image
4. **SDK Gen** — Regenerate SDKs (master branch only)
