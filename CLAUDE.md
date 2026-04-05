# CLAUDE.md — client-hub

## Project Overview

**Client Hub** is a centralized, business-agnostic MariaDB database serving as a single source of truth for client data, prospect data, orders/bookings, marketing channels, and communication preferences. It includes a wrapper REST API layer that external programs (Chatwoot, InvoiceNinja, CTI systems, chatbots) use to read and write data.

- **App location:** `~/docker/client-hub/`
- **Local URL:** http://10.0.1.220:8800 (API — not yet active)
- **MariaDB port:** 3307 (mapped from container 3306)
- **Public URL:** None (will be exposed after API layer is complete)
- **Current status:** Phase 1 — Data model design and MariaDB setup

## Architecture

### Containers

| Container | Image | Port (host:container) | Purpose |
|---|---|---|---|
| client-hub-db | mariadb:11 | 3307:3306 | MariaDB database |
| client-hub-api | TBD | 8800:8800 | REST API wrapper (Phase 2) |

### Volumes

| Volume | Path | Purpose |
|---|---|---|
| db-data | `./data/mariadb/` | MariaDB data directory |
| db-init | `./init/` | SQL initialization scripts |
| db-backups | `./backups/` | Database backup files |

### Key Directories

```
client-hub/
├── data/mariadb/     # MariaDB data (git-ignored)
├── init/             # SQL schema and seed scripts
├── backups/          # Database backups (git-ignored)
├── api/              # API source code (Phase 2)
├── docs/             # RST documentation
├── upgrades/         # Pre-upgrade analysis documents
└── screenshots/      # Local-only reference (git-ignored)
```

## Compose Files

- `docker-compose.yml` — Main compose file with MariaDB service

## Integration Points

| System | Direction | Mechanism | Status |
|---|---|---|---|
| Chatwoot | Bidirectional | REST API webhooks | Planned |
| InvoiceNinja | Inbound | REST API webhooks | Planned |
| CTI (Telephony) | Outbound query | REST API GET | Planned |
| Website Chatbot | Via Chatwoot | REST API | Planned |

## Key Commands

```bash
# Status
cd ~/docker/client-hub && docker compose ps

# Logs
docker compose logs --tail=50
docker compose logs --tail=50 client-hub-db

# Start / Stop / Restart
docker compose up -d
docker compose down
docker compose restart client-hub-db

# Connect to MariaDB
docker compose exec client-hub-db mariadb -u clienthub -p clienthub_db

# Backup database
docker compose exec client-hub-db mariadb-dump -u root -p clienthub_db > backups/clienthub_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker compose exec -T client-hub-db mariadb -u root -p clienthub_db < backups/FILENAME.sql
```

## Troubleshooting

```bash
# Check container health
docker compose ps

# View recent logs
docker compose logs --tail=50

# Check MariaDB specifically
docker compose logs --tail=50 client-hub-db

# Test MariaDB connectivity
docker compose exec client-hub-db mariadb -u clienthub -p -e "SELECT 1;"

# Check disk usage
docker system df -v 2>&1 | grep client-hub

# Check MariaDB status variables
docker compose exec client-hub-db mariadb -u root -p -e "SHOW STATUS LIKE 'Threads%';"

# Restart MariaDB
docker compose restart client-hub-db

# Full recreate (preserves data volume)
docker compose down && docker compose up -d
```

## Data Model Design Principles

- **Business-agnostic:** No business-specific columns; use configurable metadata patterns
- **Third Normal Form (3NF):** Fully normalized, no transitive dependencies
- **Multi-tenant ready:** Business/tenant isolation from day one
- **Audit trail:** Track all changes with created_at/updated_at/created_by
- **Soft deletes:** Use is_active/deleted_at rather than hard deletes
