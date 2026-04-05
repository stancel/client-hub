.. _client-hub-api-design:

######################################################################
Client Hub — REST API Design
######################################################################

.. _client-hub-api-overview:

**********************************************************************
Overview
**********************************************************************

The Client Hub API is a RESTful convenience layer around the MariaDB
database. This project follows a **data-first approach**: the database
schema is the primary product. Both DB-level integration (direct SQL
from other containers on ``my-main-net``) and API-level integration
are valid patterns depending on the task.

The API provides structured access for external systems that need
HTTP endpoints (webhooks, CTI, chatbots), while the database views
(``v_contact_summary``, ``v_contact_last_order``) provide the same
intelligence directly via SQL for internal tools and MCP access.

**Framework:** Python FastAPI

- Async-native, high performance
- Automatic OpenAPI/Swagger documentation
- Pydantic models for request/response validation
- Easy to containerize, lightweight
- SQLAlchemy for database access

**Base URL:** ``http://10.0.1.220:8800/api/v1``

**Authentication:** API key via ``X-API-Key`` header (Phase 1).
OAuth2/JWT planned for Phase 2 when public exposure is needed.

.. _client-hub-api-conventions:

**********************************************************************
API Conventions
**********************************************************************

- All responses are JSON
- Dates use ISO 8601 format (``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SS``)
- Pagination: ``?page=1&per_page=25`` (default 25, max 100)
- Sorting: ``?sort=field&order=asc|desc``
- Filtering: ``?field=value`` on applicable endpoints
- UUIDs are used in URLs (not auto-increment IDs)
- Successful responses: ``200 OK``, ``201 Created``, ``204 No Content``
- Error responses follow RFC 7807 Problem Details format

Standard error response:

.. code-block:: json

   {
     "type": "https://clienthub.local/errors/not-found",
     "title": "Contact not found",
     "status": 404,
     "detail": "No contact with UUID a1b2c3d4-..."
   }

.. _client-hub-api-endpoints:

**********************************************************************
Endpoints
**********************************************************************

.. _client-hub-api-lookup:

Integration Lookup Endpoints
======================================================================

These are the highest-priority endpoints — they support the CTI,
Chatwoot, and other real-time integration use cases.

.. _client-hub-api-lookup-phone:

GET /api/v1/lookup/phone/{number}
----------------------------------------------------------------------

**CTI Use Case:** Incoming call → identify caller instantly.

Searches ``contact_phones`` and ``org_phones`` by phone number.
Returns the matching contact(s) with their full profile.

**Path parameter:**

- ``number`` — Phone number (E.164 or partial match)

**Query parameters:**

- ``exact`` — Boolean (default ``true``). If false, uses LIKE match.

**Response (200):**

.. code-block:: json

   {
     "matches": [
       {
         "uuid": "a1b2c3d4-...",
         "first_name": "Sarah",
         "last_name": "Johnson",
         "display_name": null,
         "contact_type": "client",
         "organization": null,
         "phone": {
           "number": "+15555550101",
           "type": "mobile",
           "is_primary": true,
           "is_verified": true
         },
         "recent_orders": [
           {
             "order_number": "ORD-2026-002",
             "status": "in_progress",
             "total": "270.63",
             "order_date": "2026-03-25"
           }
         ],
         "recent_communications": [
           {
             "channel": "sms",
             "direction": "outbound",
             "subject": null,
             "occurred_at": "2025-12-20T14:35:00"
           }
         ],
         "tags": ["VIP Customer", "Repeat Customer"],
         "channel_preferences": {
           "sms": {"preferred": true, "opt_in": "opted_in"},
           "email": {"preferred": false, "opt_in": "opted_in"},
           "phone": {"preferred": false, "opt_in": "opted_out"}
         }
       }
     ],
     "count": 1
   }

**Response (404):** No match found.

.. _client-hub-api-lookup-email:

GET /api/v1/lookup/email/{email}
----------------------------------------------------------------------

**Chatwoot Use Case:** Incoming message → identify sender.

Same response format as phone lookup but searches
``contact_emails`` and ``org_emails``.

.. _client-hub-api-contacts:

Contacts CRUD
======================================================================

.. _client-hub-api-contacts-list:

GET /api/v1/contacts
----------------------------------------------------------------------

List contacts with pagination, filtering, and sorting.

**Query parameters:**

- ``page``, ``per_page`` — Pagination
- ``type`` — Filter by contact type code (client, prospect, lead, etc.)
- ``enrichment_status`` — Filter by enrichment status
- ``search`` — Full-text search across name, email, phone
- ``organization_id`` — Filter by organization UUID
- ``is_active`` — Boolean filter (default: true)
- ``sort`` — Sort field (default: last_name)
- ``order`` — asc or desc

**Response (200):**

.. code-block:: json

   {
     "data": [
       {
         "uuid": "...",
         "first_name": "Sarah",
         "last_name": "Johnson",
         "contact_type": "client",
         "enrichment_status": "complete",
         "is_active": true,
         "created_at": "2026-01-15T09:00:00"
       }
     ],
     "pagination": {
       "page": 1,
       "per_page": 25,
       "total": 42,
       "total_pages": 2
     }
   }

.. _client-hub-api-contacts-get:

GET /api/v1/contacts/{uuid}
----------------------------------------------------------------------

Get a single contact with all related data.

**Response (200):** Full contact object including phones, emails,
addresses, channel preferences, marketing sources, tags, notes,
recent orders, and recent communications.

.. _client-hub-api-contacts-create:

POST /api/v1/contacts
----------------------------------------------------------------------

Create a new contact.

**Request body:**

.. code-block:: json

   {
     "first_name": "Emily",
     "last_name": "Rodriguez",
     "contact_type": "lead",
     "organization_uuid": null,
     "phones": [
       {"number": "+15555550301", "type": "mobile", "is_primary": true}
     ],
     "emails": [
       {"address": "emily@example.com", "type": "personal", "is_primary": true}
     ],
     "marketing_sources": ["website"],
     "data_source": "website_form"
   }

**Response (201):** Created contact object with UUID.

.. _client-hub-api-contacts-update:

PUT /api/v1/contacts/{uuid}
----------------------------------------------------------------------

Update a contact. Partial updates supported (only send changed fields).

.. _client-hub-api-contacts-convert:

POST /api/v1/contacts/{uuid}/convert
----------------------------------------------------------------------

**Convert a prospect/lead to a client.** Sets ``contact_type_id`` to
client, records ``converted_at`` and ``converted_from_type_id``.

**Request body:**

.. code-block:: json

   {
     "notes": "Converted after first order placed"
   }

**Response (200):** Updated contact with conversion details.

.. _client-hub-api-contacts-delete:

DELETE /api/v1/contacts/{uuid}
----------------------------------------------------------------------

Soft-delete a contact (sets ``is_active=false``, ``deleted_at=NOW()``).

.. _client-hub-api-organizations:

Organizations CRUD
======================================================================

- ``GET /api/v1/organizations`` — List with pagination
- ``GET /api/v1/organizations/{uuid}`` — Get with contacts, phones,
  emails, addresses
- ``POST /api/v1/organizations`` — Create
- ``PUT /api/v1/organizations/{uuid}`` — Update
- ``DELETE /api/v1/organizations/{uuid}`` — Soft-delete

.. _client-hub-api-orders:

Orders CRUD
======================================================================

- ``GET /api/v1/orders`` — List with filters (status, contact, date range)
- ``GET /api/v1/orders/{uuid}`` — Get with items, status history,
  invoices, payments
- ``POST /api/v1/orders`` — Create order with line items
- ``PUT /api/v1/orders/{uuid}`` — Update order details
- ``POST /api/v1/orders/{uuid}/status`` — Change order status
  (creates history record)
- ``DELETE /api/v1/orders/{uuid}`` — Soft-delete

.. _client-hub-api-preferences:

Contact Preferences
======================================================================

- ``GET /api/v1/contacts/{uuid}/preferences`` — List all preferences
- ``GET /api/v1/contacts/{uuid}/preferences/{key}`` — Get one
- ``PUT /api/v1/contacts/{uuid}/preferences/{key}`` — Set/update
- ``DELETE /api/v1/contacts/{uuid}/preferences/{key}`` — Remove

.. _client-hub-api-marketing:

Marketing Opt-Outs
======================================================================

- ``GET /api/v1/contacts/{uuid}/marketing`` — Get opt-out flags
- ``PUT /api/v1/contacts/{uuid}/marketing`` — Update opt-out flags

**Request body:**

.. code-block:: json

   {
     "opt_out_sms": true,
     "opt_out_email": false,
     "opt_out_phone": true
   }

.. _client-hub-api-intelligence:

Customer Intelligence
======================================================================

These endpoints surface the same data as the database views
(``v_contact_summary``, ``v_contact_last_order``) through the API.

- ``GET /api/v1/contacts/{uuid}/summary`` — Full intelligence
  summary (lifetime value, order stats, communication stats,
  marketing sources, tags, opt-outs, outstanding balance)
- ``GET /api/v1/contacts/{uuid}/last-order`` — Last order details
  (order number, date, status, total, item types/descriptions)
- ``GET /api/v1/intelligence/marketable`` — List contacts who have
  NOT opted out of a given channel. Query param: ``channel=sms|email|phone``
- ``GET /api/v1/intelligence/needs-enrichment`` — Contacts with
  ``enrichment_status`` = ``partial`` or ``needs_review``
- ``GET /api/v1/intelligence/outstanding-balances`` — Contacts with
  unpaid invoice balances

.. _client-hub-api-invoices:

Invoices & Payments
======================================================================

- ``GET /api/v1/invoices`` — List with filters
- ``GET /api/v1/invoices/{uuid}`` — Get with payments
- ``POST /api/v1/invoices`` — Create invoice for an order
- ``PUT /api/v1/invoices/{uuid}`` — Update invoice
- ``POST /api/v1/invoices/{uuid}/payments`` — Record a payment
- ``GET /api/v1/payments`` — List payments with filters
- ``GET /api/v1/payments/{uuid}`` — Get payment detail

.. _client-hub-api-communications:

Communications
======================================================================

- ``GET /api/v1/communications`` — List with filters (contact, channel,
  date range, direction)
- ``GET /api/v1/communications/{uuid}`` — Get detail
- ``POST /api/v1/communications`` — Log a communication

.. _client-hub-api-webhooks:

Webhook Endpoints
======================================================================

These endpoints receive events from external systems and translate
them into database operations.

.. _client-hub-api-webhook-invoiceninja:

POST /api/v1/webhooks/invoiceninja
----------------------------------------------------------------------

**InvoiceNinja integration.** Receives webhook payloads for:

- ``payment.created`` — Record payment, update invoice balance
- ``invoice.updated`` — Sync invoice status
- ``client.updated`` — Sync contact info changes (email, phone, address)

**Request body:** InvoiceNinja webhook payload (JSON).

**Processing logic:**

1. Validate webhook signature (if configured)
2. Match contact by ``external_refs_json.invoiceninja`` ID
3. Apply changes to the matching records
4. Return ``200 OK`` with processing summary

.. _client-hub-api-webhook-chatwoot:

POST /api/v1/webhooks/chatwoot
----------------------------------------------------------------------

**Chatwoot integration.** Receives webhook payloads for:

- ``message_created`` — Log communication, identify contact
- ``contact_created`` — Create or match prospect/lead
- ``contact_updated`` — Sync contact info changes
- ``conversation_resolved`` — Update communication records

**Processing logic:**

1. Extract sender phone/email from payload
2. Look up or create contact
3. Log communication record
4. Return ``200 OK``

.. _client-hub-api-business:

Business Settings
======================================================================

- ``GET /api/v1/settings`` — Get business configuration
- ``PUT /api/v1/settings`` — Update business configuration

.. _client-hub-api-health:

Health & Utility
======================================================================

- ``GET /api/v1/health`` — Health check (DB connectivity, uptime)
- ``GET /api/v1/stats`` — Dashboard stats (contact counts by type,
  order counts by status, revenue summary)

.. _client-hub-api-docker:

**********************************************************************
Docker Configuration
**********************************************************************

The API runs as a Python FastAPI container on ``my-main-net``.

.. code-block:: yaml

   services:
     client-hub-api:
       build:
         context: ./api
         dockerfile: Dockerfile
       container_name: client-hub-api
       restart: unless-stopped
       ports:
         - "8800:8800"
       environment:
         DB_HOST: mariadb
         DB_PORT: 3306
         DB_NAME: ${DB_NAME:-dev_schema}
         DB_USER: ${DB_USER:-clienthub}
         DB_PASSWORD: ${DB_PASSWORD}
         API_KEY: ${API_KEY}
         API_HOST: 0.0.0.0
         API_PORT: 8800
       networks:
         - my-main-net
       depends_on: []

   networks:
     my-main-net:
       external: true

.. _client-hub-api-project-structure:

**********************************************************************
API Project Structure
**********************************************************************

.. code-block:: text

   api/
   ├── Dockerfile
   ├── requirements.txt
   ├── app/
   │   ├── __init__.py
   │   ├── main.py              # FastAPI app, middleware, startup
   │   ├── config.py            # Settings from env vars
   │   ├── database.py          # SQLAlchemy engine/session
   │   ├── models/              # SQLAlchemy ORM models
   │   │   ├── __init__.py
   │   │   ├── contact.py
   │   │   ├── organization.py
   │   │   ├── order.py
   │   │   ├── invoice.py
   │   │   ├── communication.py
   │   │   └── lookups.py
   │   ├── schemas/             # Pydantic request/response schemas
   │   │   ├── __init__.py
   │   │   ├── contact.py
   │   │   ├── organization.py
   │   │   ├── order.py
   │   │   ├── invoice.py
   │   │   ├── communication.py
   │   │   └── common.py
   │   ├── routers/             # Endpoint route handlers
   │   │   ├── __init__.py
   │   │   ├── lookup.py        # /lookup/phone, /lookup/email
   │   │   ├── contacts.py
   │   │   ├── organizations.py
   │   │   ├── orders.py
   │   │   ├── invoices.py
   │   │   ├── communications.py
   │   │   ├── webhooks.py      # /webhooks/invoiceninja, /webhooks/chatwoot
   │   │   ├── settings.py
   │   │   └── health.py
   │   ├── services/            # Business logic layer
   │   │   ├── __init__.py
   │   │   ├── contact_service.py
   │   │   ├── order_service.py
   │   │   ├── lookup_service.py
   │   │   └── webhook_service.py
   │   └── middleware/
   │       ├── __init__.py
   │       └── auth.py          # API key validation
   └── tests/
       ├── __init__.py
       ├── conftest.py
       ├── test_lookup.py
       ├── test_contacts.py
       └── test_webhooks.py
