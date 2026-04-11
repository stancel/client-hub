.. _client-hub-todo:

######################################################################
Client Hub — TODO
######################################################################

.. _client-hub-todo-phase1:

Phase 1 — Data Model Design [COMPLETE]
======================================================================

- [x] Design 3NF data model (31 tables + 2 views)
- [x] Document all tables, columns, types, constraints, indexes, FKs
- [x] Document normalization rationale (1NF, 2NF, 3NF analysis)
- [x] Document junction tables and why they exist
- [x] Include entity-relationship summary
- [x] Write comprehensive ``docs/data-model.rst``
- [x] Add marketing opt-out boolean flags (sms, email, phone)
- [x] Add contact_preferences table (flexible key-value)
- [x] Create v_contact_summary and v_contact_last_order views

.. _client-hub-todo-phase2:

Phase 2 — Schema Implementation [COMPLETE]
======================================================================

- [x] Create ``migrations/`` directory with numbered SQL files
- [x] Write DDL for all 31 tables and 2 views (migrations 001-013)
- [x] Execute all migrations against ``dev_schema`` via MCP tools
- [x] Verify schema with ``search_objects`` MCP tool
- [x] Seed lookup tables with initial reference data (58 rows)

.. _client-hub-todo-phase3:

Phase 3 — Test Data and Validation [COMPLETE]
======================================================================

- [x] Insert realistic test data exercising all relationships
- [x] Ran 11 validation queries — all passed with zero issues
- [x] Validated: FK integrity, orphan checks, CTI/Chatwoot lookups,
  conversion flow, order chain, junction tables, opt-outs, provenance

.. _client-hub-todo-phase4:

Phase 4 — REST API Design [COMPLETE]
======================================================================

- [x] Create ``docs/api-design.rst``
- [x] Design CTI lookup endpoints (phone, email)
- [x] Design CRUD endpoints for all core entities
- [x] Design webhook endpoints (InvoiceNinja, Chatwoot)
- [x] Design preference and marketing opt-out endpoints
- [x] Design customer intelligence endpoints
- [x] Define authentication approach (API key)
- [x] Choose API framework (Python FastAPI + SQLAlchemy)
- [x] Document TDD testing strategy
- [x] Document SDK generation workflow (Python, PHP, TypeScript)
- [x] **GATE: Brad approved the design**

.. _client-hub-todo-phase5:

Phase 5 — API Implementation (TDD) [COMPLETE]
======================================================================

63 tests passing across 13 test files, 23 endpoint paths live.

- [x] Scaffold API project in ``api/`` directory
- [x] Set up pytest + httpx test infrastructure with real DB
- [x] Implement and test: health, lookup, contacts CRUD, conversion,
  preferences, marketing opt-outs, intelligence, organizations,
  orders, invoices, payments, communications, webhooks, settings
- [x] Add API container to ``docker-compose.yml`` on ``my-main-net``
- [x] Container running, all endpoints verified with curl
- [x] OpenAPI spec at ``/openapi.json`` (23 paths)

.. _client-hub-todo-phase6:

Phase 6 — SDK Generation [COMPLETE]
======================================================================

- [x] Created ``scripts/generate-sdks.sh`` (Docker-based)
- [x] Generated Python SDK in ``sdks/python/``
- [x] Generated PHP SDK in ``sdks/php/``
- [x] Generated TypeScript SDK in ``sdks/typescript/``
- [x] All SDKs have 10 API classes matching every router

.. _client-hub-todo-phase7:

Phase 7 — CI/CD Pipeline [COMPLETE]
======================================================================

- [x] GitHub Actions CI: ``.github/workflows/ci.yml``
- [x] Pipeline: lint (ruff + rstcheck) → test (MariaDB service) →
  build → SDK generation
- [x] ruff lint config, all Python code passing
- [x] All RST docs passing rstcheck
- [x] Documented in ``docs/ci-cd.rst``

.. _client-hub-todo-phase8:

Phase 8 — Multi-Source + Installer [COMPLETE]
======================================================================

- [x] Migrations 014-018 (sources, api_keys, source_id columns,
  channel types, views, tracking table)
- [x] Multi-source auth middleware (root key + per-source keys)
- [x] Admin router for sources and API key management
- [x] Auto-stamp source_id on contacts and communications
- [x] 78 tests passing (63 original + 15 new)
- [x] One-line installer (``scripts/install.sh``)
- [x] Bundled Docker compose files (with/without TLS)
- [x] Backup, uninstall, smoke-test, migration runner scripts
- [x] Full documentation: Multi-Source, Deployment, Cross-Project
  Integration, Data Privacy, Upgrade guide
- [x] Updated CI workflow with shellcheck + new migrations

.. _client-hub-todo-future:

Future — Planned Work
======================================================================

- [ ] Deploy first production instance (Complete Dental Care VPS)
- [ ] InvoiceNinja webhook integration (live)
- [ ] Chatwoot webhook integration (live)
- [ ] SIP/Phone CTI integration (live caller lookup)
- [ ] Zammad customer support integration
- [ ] Marketing campaign platform integration
- [ ] Scheduling form integration
- [ ] Web scraping / enrichment API integration
- [ ] Online booking portal (prospect self-registration)
- [x] Expose API via Caddy with auto-TLS (bundled compose)
- [x] Automated database backups (nightly cron)
- [ ] Monitoring and alerting
- [ ] Data retention / PII purge automation
- [ ] Rate limiting on admin endpoints
