.. _client-hub-todo:

######################################################################
Client Hub — TODO
######################################################################

.. _client-hub-todo-phase1:

Phase 1 — Data Model and Database Setup
======================================================================

- [ ] Design 3NF data model (entities: businesses, contacts, orders,
  channels, communications, addresses, notes)
- [ ] Create SQL schema initialization scripts in ``init/``
- [ ] Create ``.env`` from ``.env.example`` with real credentials
- [ ] Start MariaDB container and verify connectivity
- [ ] Load schema and verify all tables, constraints, indexes
- [ ] Add seed data for initial testing

.. _client-hub-todo-phase2:

Phase 2 — REST API Wrapper
======================================================================

- [ ] Choose API framework (Python FastAPI, Go, Node.js, etc.)
- [ ] Scaffold API project in ``api/`` directory
- [ ] Implement CRUD endpoints for all core entities
- [ ] Add authentication/authorization layer
- [ ] Add API container to ``docker-compose.yml``
- [ ] Write API documentation (OpenAPI/Swagger)

.. _client-hub-todo-phase3:

Phase 3 — External Integrations
======================================================================

- [ ] Chatwoot webhook integration (inbound + outbound)
- [ ] InvoiceNinja webhook integration (payment events)
- [ ] CTI caller lookup endpoint
- [ ] Website chatbot integration via Chatwoot

.. _client-hub-todo-phase4:

Phase 4 — Production Readiness
======================================================================

- [ ] Expose API via Nginx Proxy Manager with SSL
- [ ] Set up automated database backups
- [ ] Add monitoring and health check endpoints
- [ ] Load testing and performance tuning
- [ ] Security audit of API endpoints
