.. _client-hub-todo:

######################################################################
Client Hub — TODO
######################################################################

.. _client-hub-todo-phase1:

Phase 1 — Data Model Design [COMPLETE]
======================================================================

- [x] Design 3NF data model (30 tables: 17 entity, 2 junction, 11 lookup)
- [x] Document all tables, columns, types, constraints, indexes, FKs
- [x] Document normalization rationale (1NF, 2NF, 3NF analysis)
- [x] Document junction tables and why they exist
- [x] Include entity-relationship summary
- [x] Write comprehensive ``docs/data-model.rst``

.. _client-hub-todo-phase2:

Phase 2 — Schema Implementation [COMPLETE]
======================================================================

- [x] Create ``migrations/`` directory with numbered SQL files
- [x] Write DDL for lookup tables (dependency-free, created first)
- [x] Write DDL for core entity tables (contacts, organizations)
- [x] Write DDL for contact detail tables (phones, emails, addresses)
- [x] Write DDL for junction tables
- [x] Write DDL for orders, order_items, order_status_history
- [x] Write DDL for invoices, payments
- [x] Write DDL for communications, contact_notes
- [x] Execute all migrations against ``dev_schema`` via MCP tools
- [x] Verify schema with ``search_objects`` MCP tool (30 tables, 36 FKs)
- [x] Seed lookup tables with initial reference data (58 rows)

.. _client-hub-todo-phase3:

Phase 3 — Test Data and Validation [COMPLETE]
======================================================================

- [x] Create seed data exercising all relationships and edge cases
- [x] Insert test clients, prospects, orders, bookings, communications
- [x] Validate all foreign keys resolve correctly (0 orphans)
- [x] Validate no orphaned records across all 10 child tables
- [x] Test prospect-to-client conversion flow (James Smith)
- [x] Test CTI phone number lookup use case
- [x] Test Chatwoot email lookup use case
- [x] Test junction tables (tags, marketing sources)
- [x] Test order→invoice→payment chain
- [x] Test channel preferences with opt-in compliance
- [x] Test data provenance tracking (enriched vs manual)
- [x] Test order status history audit trail
- [x] All 11 validations passed with zero issues

.. _client-hub-todo-phase4:

Phase 4 — REST API Design
======================================================================

- [ ] Create ``docs/api-design.rst``
- [ ] Design CTI lookup endpoints (phone, email)
- [ ] Design CRUD endpoints for all core entities
- [ ] Design webhook endpoints (InvoiceNinja, Chatwoot)
- [ ] Define authentication/authorization approach
- [ ] Choose API framework
- [ ] **GATE: Get Brad's approval before implementing**

.. _client-hub-todo-phase5:

Phase 5 — API Implementation
======================================================================

- [ ] Scaffold API project in ``api/`` directory
- [ ] Implement all endpoints
- [ ] Add API container to ``docker-compose.yml`` on ``my-main-net``
- [ ] Write integration tests against real database
- [ ] Test all webhook/lookup scenarios with curl
- [ ] Document all endpoints with example requests/responses
