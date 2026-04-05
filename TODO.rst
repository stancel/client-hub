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

Phase 2 — Schema Implementation [IN PROGRESS]
======================================================================

- [ ] Create ``migrations/`` directory with numbered SQL files
- [ ] Write DDL for lookup tables (dependency-free, created first)
- [ ] Write DDL for core entity tables (contacts, organizations)
- [ ] Write DDL for contact detail tables (phones, emails, addresses)
- [ ] Write DDL for junction tables
- [ ] Write DDL for orders, order_items, order_status_history
- [ ] Write DDL for invoices, payments
- [ ] Write DDL for communications, contact_notes
- [ ] Execute all migrations against ``dev_schema`` via MCP tools
- [ ] Verify schema with ``search_objects`` MCP tool
- [ ] Seed lookup tables with initial reference data

.. _client-hub-todo-phase3:

Phase 3 — Test Data and Validation
======================================================================

- [ ] Create seed data exercising all relationships and edge cases
- [ ] Insert test clients, prospects, orders, bookings, communications
- [ ] Validate all foreign keys resolve correctly
- [ ] Validate no orphaned records
- [ ] Test prospect-to-client conversion flow
- [ ] Test CTI phone number lookup use case
- [ ] Test Chatwoot email lookup use case
- [ ] Test junction tables (tags, marketing sources)
- [ ] Document and fix any issues found

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
