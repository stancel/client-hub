.. _client-hub-changelog:

######################################################################
Client Hub — Changelog
######################################################################

.. _client-hub-changelog-2026-04-05b:

2026-04-05 — Align with Shared MariaDB Infrastructure
======================================================================

- Removed standalone MariaDB container from ``docker-compose.yml``
- Switched to shared MariaDB 12.2.2 at ``~/docker/mariadb/`` on port
  3306 via ``my-main-net``
- Updated all docs to reference shared MariaDB and MySQL MCP Server
  (DBHub) for schema design workflow
- ``docker-compose.yml`` now a placeholder for Phase 2 API container
- Updated ``.env.example`` with simplified DB credentials

.. _client-hub-changelog-2026-04-05:

2026-04-05 — Initial Project Scaffolding
======================================================================

- Created project scaffolding with all standard files (CLAUDE.md,
  README.rst, CHANGELOG.rst, TODO.rst, docs/, .gitignore)
- Added ``docker-compose.yml`` (initially with standalone MariaDB)
- Added ``.env.example`` with database credential templates
- Created ``docs/architecture.rst`` with detailed architecture docs
- Created ``init/`` directory for SQL initialization scripts
- Project status: Phase 1 — Data model design
