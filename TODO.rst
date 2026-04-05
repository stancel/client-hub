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

Phase 5 — API Implementation (TDD)
======================================================================

Every endpoint must have a test written before or alongside it.

- [ ] Scaffold API project in ``api/`` directory
- [ ] Set up pytest + httpx test infrastructure with real DB
- [ ] Implement and test: health endpoint
- [ ] Implement and test: phone lookup (CTI)
- [ ] Implement and test: email lookup (Chatwoot)
- [ ] Implement and test: contacts CRUD
- [ ] Implement and test: contact conversion (prospect → client)
- [ ] Implement and test: contact preferences CRUD
- [ ] Implement and test: marketing opt-out management
- [ ] Implement and test: customer intelligence endpoints
- [ ] Implement and test: organizations CRUD
- [ ] Implement and test: orders CRUD + status changes
- [ ] Implement and test: invoices + payments
- [ ] Implement and test: communications log
- [ ] Implement and test: InvoiceNinja webhook
- [ ] Implement and test: Chatwoot webhook
- [ ] Implement and test: business settings
- [ ] Add API container to ``docker-compose.yml`` on ``my-main-net``
- [ ] Start container, verify all endpoints with curl
- [ ] Verify OpenAPI spec at ``/openapi.json``

.. _client-hub-todo-phase6:

Phase 6 — SDK Generation
======================================================================

- [ ] Create ``scripts/generate-sdks.sh`` script
- [ ] Set up openapi-generator-cli (Docker-based, no local Java)
- [ ] Generate Python SDK in ``sdks/python/``
- [ ] Generate PHP SDK in ``sdks/php/``
- [ ] Generate TypeScript SDK in ``sdks/typescript/``
- [ ] Test generated SDKs against running API
- [ ] Document SDK usage in each SDK's README

.. _client-hub-todo-phase7:

Phase 7 — CI/CD Pipeline (TDD)
======================================================================

- [ ] Create CI pipeline configuration (GitHub Actions or similar)
- [ ] Pipeline stages:

  1. Lint (ruff/flake8 for Python, rstcheck for docs)
  2. Run full pytest suite against test database
  3. Build Docker image
  4. Regenerate SDKs from OpenAPI spec
  5. Deploy (when targeting production)

- [ ] Set up test database provisioning for CI
- [ ] Add pre-commit hooks for lint + test
- [ ] Document CI/CD workflow in ``docs/ci-cd.rst``

.. _client-hub-todo-future:

Future — Planned Integrations
======================================================================

- [ ] InvoiceNinja webhook integration (live)
- [ ] Chatwoot webhook integration (live)
- [ ] SIP/Phone CTI integration (live caller lookup)
- [ ] Zammad customer support integration
- [ ] Marketing campaign platform integration
- [ ] Scheduling form integration
- [ ] Web scraping / enrichment API integration
- [ ] Online booking portal (prospect self-registration)
- [ ] Expose API via Nginx Proxy Manager with SSL
- [ ] Automated database backups
- [ ] Monitoring and alerting
