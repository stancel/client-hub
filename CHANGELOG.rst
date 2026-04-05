.. _client-hub-changelog:

######################################################################
Client Hub — Changelog
######################################################################

.. _client-hub-changelog-2026-04-05c:

2026-04-05 — Phase 1 Complete: Data Model Design
======================================================================

- Created comprehensive ``docs/data-model.rst`` (30 tables total)
- 17 entity tables: business_settings, contacts, organizations,
  contact_phones, contact_emails, contact_addresses, org_phones,
  org_emails, org_addresses, contact_channel_prefs, contact_notes,
  orders, order_items, order_status_history, invoices, payments,
  communications
- 2 junction tables: contact_tag_map, contact_marketing_sources
- 11 lookup tables: contact_types, phone_types, email_types,
  address_types, channel_types, marketing_sources, order_statuses,
  order_item_types, invoice_statuses, payment_methods, tags
- Full 3NF normalization analysis with documented denormalization
  decisions
- Corrected tenant model: single-tenant (one DB per business), not
  multi-tenant
- Development database: ``dev_schema`` on shared MariaDB

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
