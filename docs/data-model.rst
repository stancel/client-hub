.. _client-hub-data-model:

######################################################################
Client Hub — Data Model
######################################################################

.. _client-hub-dm-overview:

**********************************************************************
Overview
**********************************************************************

This document defines the complete data model for Client Hub, a
business-agnostic client and prospect management database. The schema
is designed to be deployed as a single-tenant database (one database
per business). All tables are normalized to Third Normal Form (3NF).

**Design date:** 2026-04-05

.. _client-hub-dm-design-principles:

**********************************************************************
Design Principles
**********************************************************************

1. **Single-tenant** — One database instance per business. The
   ``business_settings`` table stores configuration for the owning
   business, not multi-tenant isolation.

2. **Third Normal Form (3NF)** — Every non-key column depends on
   the key, the whole key, and nothing but the key. No transitive
   dependencies.

3. **Business-agnostic** — No industry-specific columns. Service
   types, product categories, and status labels are stored in
   configurable lookup tables.

4. **Referential integrity** — All foreign keys enforced at the
   database level with appropriate ON DELETE/ON UPDATE rules.

5. **Audit columns** — Every table includes ``created_at``,
   ``updated_at``, and ``created_by`` (nullable for system inserts).

6. **Soft deletes** — ``is_active`` BOOLEAN (default TRUE) and
   ``deleted_at`` DATETIME (nullable) on all entity tables.

7. **Data provenance** — Contact details track their source, whether
   they were enriched or manually entered, and when last verified.

8. **UUID-friendly** — Primary keys use ``BIGINT UNSIGNED AUTO_INCREMENT``
   for performance. External-facing IDs (API responses) can use a
   separate ``uuid`` CHAR(36) column where needed.

.. _client-hub-dm-er-summary:

**********************************************************************
Entity-Relationship Summary
**********************************************************************

Core entity groups and their relationships:

::

  business_settings (1 row per database — singleton config)

  contacts ──────────────────── contact_types (lookup)
    │  A contact is a person: client, prospect, lead, vendor, etc.
    │  contact_type determines their status.
    │  Prospect → Client transition = update contact_type_id + set
    │  converted_at timestamp.
    │
    ├── contact_phones (1:M)       phone numbers with type labels
    ├── contact_emails (1:M)       email addresses with type labels
    ├── contact_addresses (1:M)    physical addresses with type labels
    ├── contact_tags (M:M)         via contact_tag_map junction
    ├── contact_notes (1:M)        free-text notes
    │
    ├── contact_channel_prefs (1:M per channel)
    │     preferred communication channels + opt-in/opt-out
    │
    ├── contact_marketing_sources (M:M)
    │     via contact_marketing_source junction
    │     how they found us (Google, referral, walk-in, etc.)
    │
    └── organizations (M:1)
          A contact can belong to one organization.
          Organizations have their own addresses.

  organizations
    ├── org_phones (1:M)
    ├── org_emails (1:M)
    ├── org_addresses (1:M)
    └── contacts (1:M)

  orders ─────────────────────── contacts (M:1, required)
    │  An order/booking belongs to one contact.
    │  Status: quoted, confirmed, in_progress, completed, cancelled.
    │
    ├── order_items (1:M)        line items with pricing
    ├── order_status_history (1:M)  status change audit trail
    │
    └── invoices (1:M)
          An order can have multiple invoices (deposits, final, etc.)
          │
          └── payments (1:M)
                Payment records against an invoice.

  communications (log)
    │  Records every interaction (call, email, SMS, chat, etc.)
    │  Links to a contact (required).
    │  Links to an order (optional).
    └── References channel_type lookup.

  Lookup / Reference tables:
    - contact_types        (client, prospect, lead, vendor, other)
    - phone_types          (mobile, home, work, fax, other)
    - email_types          (personal, work, billing, other)
    - address_types        (home, work, billing, shipping, other)
    - channel_types        (sms, email, phone, chat, portal, in_person)
    - marketing_sources    (google, social_media, referral, walk_in, ...)
    - order_statuses       (quoted, confirmed, in_progress, completed, ...)
    - order_item_types     (product, service, booking, other)
    - invoice_statuses     (draft, sent, paid, partial, overdue, void)
    - payment_methods      (cash, credit_card, debit_card, check, ...)
    - tags                 (user-defined labels for contacts)

.. _client-hub-dm-tables:

**********************************************************************
Table Definitions
**********************************************************************

.. _client-hub-dm-business-settings:

business_settings
======================================================================

Singleton table holding configuration for the business that owns this
database instance.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - business_name
     - VARCHAR(255)
     - NO
     -
   * - business_type
     - VARCHAR(100)
     - YES
     - e.g., "embroidery", "dental", "lawn_care"
   * - timezone
     - VARCHAR(50)
     - NO
     - Default: 'America/Chicago'
   * - currency
     - CHAR(3)
     - NO
     - ISO 4217, default: 'USD'
   * - tax_rate
     - DECIMAL(5,4)
     - YES
     - Default tax rate (e.g., 0.0825 = 8.25%)
   * - phone
     - VARCHAR(20)
     - YES
     - Primary business phone
   * - email
     - VARCHAR(255)
     - YES
     - Primary business email
   * - website
     - VARCHAR(255)
     - YES
     -
   * - address_line1
     - VARCHAR(255)
     - YES
     -
   * - address_line2
     - VARCHAR(255)
     - YES
     -
   * - city
     - VARCHAR(100)
     - YES
     -
   * - state
     - VARCHAR(50)
     - YES
     -
   * - postal_code
     - VARCHAR(20)
     - YES
     -
   * - country
     - CHAR(2)
     - NO
     - ISO 3166-1 alpha-2, default: 'US'
   * - settings_json
     - JSON
     - YES
     - Extensible key-value config
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Normalization:** This table is in 3NF. The address fields belong
directly to the business (no separate address entity needed for a
singleton). ``settings_json`` provides extensibility without schema
changes for business-specific config.

.. _client-hub-dm-lookup-tables:

Lookup Tables
======================================================================

All lookup tables share the same structure. They are reference data
that rarely changes. Each has a ``code`` (machine-readable) and
``label`` (human-readable display name).

Common structure:

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - code
     - VARCHAR(50)
     - NO
     - UNIQUE, machine-readable key
   * - label
     - VARCHAR(100)
     - NO
     - Human display name
   * - description
     - VARCHAR(255)
     - YES
     - Optional explanation
   * - sort_order
     - INT
     - NO
     - DEFAULT 0, for display ordering
   * - is_active
     - BOOLEAN
     - NO
     - DEFAULT TRUE
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP

Tables using this structure:

- **contact_types** — client, prospect, lead, vendor, other
- **phone_types** — mobile, home, work, fax, other
- **email_types** — personal, work, billing, other
- **address_types** — home, work, billing, shipping, other
- **channel_types** — sms, email, phone, chat, portal, in_person
- **marketing_sources** — google_search, social_media_ad, referral,
  walk_in, phone_call, website, word_of_mouth, other
- **order_statuses** — quoted, confirmed, in_progress, completed,
  cancelled, on_hold
- **order_item_types** — product, service, booking, other
- **invoice_statuses** — draft, sent, paid, partial, overdue, void
- **payment_methods** — cash, credit_card, debit_card, check, bank_transfer,
  online, other
- **tags** — user-defined; no preset values

**Normalization:** Each lookup table is in 3NF. ``code`` and ``label``
are independent attributes of the lookup entry — ``label`` does not
depend on ``code`` (different businesses may relabel the same code).

.. _client-hub-dm-contacts:

contacts
======================================================================

The central entity. Every person in the system is a contact. Their
type (client, prospect, lead, vendor) is determined by
``contact_type_id``.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - uuid
     - CHAR(36)
     - NO
     - UNIQUE, for external/API use
   * - contact_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → contact_types.id
   * - organization_id
     - BIGINT UNSIGNED
     - YES
     - FK → organizations.id
   * - first_name
     - VARCHAR(100)
     - NO
     -
   * - last_name
     - VARCHAR(100)
     - NO
     -
   * - display_name
     - VARCHAR(200)
     - YES
     - Computed or override display name
   * - date_of_birth
     - DATE
     - YES
     -
   * - converted_at
     - DATETIME
     - YES
     - When prospect was converted to client
   * - converted_from_type_id
     - BIGINT UNSIGNED
     - YES
     - FK → contact_types.id (previous type before conversion)
   * - enrichment_status
     - ENUM('complete','partial','needs_review')
     - NO
     - DEFAULT 'partial'
   * - marketing_opt_out_sms
     - BOOLEAN
     - NO
     - DEFAULT FALSE. 1 = opted out of SMS/MMS marketing.
   * - marketing_opt_out_email
     - BOOLEAN
     - NO
     - DEFAULT FALSE. 1 = opted out of email marketing.
   * - marketing_opt_out_phone
     - BOOLEAN
     - NO
     - DEFAULT FALSE. 1 = opted out of phone call marketing.
   * - notes_text
     - TEXT
     - YES
     - Quick free-text notes (detailed notes in contact_notes)
   * - external_refs_json
     - JSON
     - YES
     - External system IDs: {"invoiceninja": "...", "chatwoot": "..."}
   * - is_active
     - BOOLEAN
     - NO
     - DEFAULT TRUE
   * - deleted_at
     - DATETIME
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE
   * - created_by
     - VARCHAR(100)
     - YES
     - User or system that created the record

**Indexes:**

- ``idx_contacts_uuid`` on ``uuid`` (UNIQUE)
- ``idx_contacts_type`` on ``contact_type_id``
- ``idx_contacts_org`` on ``organization_id``
- ``idx_contacts_name`` on ``last_name, first_name``
- ``idx_contacts_enrichment`` on ``enrichment_status``
- ``idx_contacts_active`` on ``is_active``

**Normalization:** 3NF. ``contact_type_id`` is a FK to a lookup table,
not a denormalized string. ``converted_from_type_id`` records the
previous type at the time of conversion — this is a historical fact
about the contact, not a transitive dependency. ``external_refs_json``
stores integration IDs that are opaque to this schema; normalizing
these into a separate table would add complexity without benefit since
they are only used for exact-match lookups by the API layer.

.. _client-hub-dm-organizations:

organizations
======================================================================

Companies, households, practices, or other groupings that contacts
can belong to.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - uuid
     - CHAR(36)
     - NO
     - UNIQUE
   * - name
     - VARCHAR(255)
     - NO
     -
   * - org_type
     - VARCHAR(100)
     - YES
     - e.g., "company", "household", "practice"
   * - website
     - VARCHAR(255)
     - YES
     -
   * - notes_text
     - TEXT
     - YES
     -
   * - external_refs_json
     - JSON
     - YES
     -
   * - is_active
     - BOOLEAN
     - NO
     - DEFAULT TRUE
   * - deleted_at
     - DATETIME
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE
   * - created_by
     - VARCHAR(100)
     - YES
     -

**Indexes:**

- ``idx_orgs_uuid`` on ``uuid`` (UNIQUE)
- ``idx_orgs_name`` on ``name``

.. _client-hub-dm-contact-phones:

contact_phones
======================================================================

Multiple phone numbers per contact with type labels and provenance.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - phone_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → phone_types.id
   * - phone_number
     - VARCHAR(20)
     - NO
     - E.164 format preferred
   * - phone_extension
     - VARCHAR(10)
     - YES
     -
   * - is_primary
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - is_verified
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - verified_at
     - DATETIME
     - YES
     -
   * - data_source
     - VARCHAR(50)
     - YES
     - e.g., "manual", "invoiceninja", "chatwoot", "enrichment"
   * - is_enriched
     - BOOLEAN
     - NO
     - DEFAULT FALSE (TRUE if filled by enrichment service)
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Indexes:**

- ``idx_cp_contact`` on ``contact_id``
- ``idx_cp_phone`` on ``phone_number`` (for CTI reverse lookup)
- ``idx_cp_primary`` on ``contact_id, is_primary``

**Normalization:** 3NF. Phone type is a FK to a lookup table.
Provenance fields (``data_source``, ``is_enriched``, ``verified_at``)
are attributes of *this phone record*, not of the contact.

.. _client-hub-dm-contact-emails:

contact_emails
======================================================================

Multiple email addresses per contact.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - email_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → email_types.id
   * - email_address
     - VARCHAR(255)
     - NO
     -
   * - is_primary
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - is_verified
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - verified_at
     - DATETIME
     - YES
     -
   * - data_source
     - VARCHAR(50)
     - YES
     -
   * - is_enriched
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Indexes:**

- ``idx_ce_contact`` on ``contact_id``
- ``idx_ce_email`` on ``email_address`` (for Chatwoot reverse lookup)
- ``idx_ce_primary`` on ``contact_id, is_primary``

.. _client-hub-dm-contact-addresses:

contact_addresses
======================================================================

Physical addresses per contact.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - address_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → address_types.id
   * - address_line1
     - VARCHAR(255)
     - NO
     -
   * - address_line2
     - VARCHAR(255)
     - YES
     -
   * - city
     - VARCHAR(100)
     - NO
     -
   * - state
     - VARCHAR(50)
     - NO
     -
   * - postal_code
     - VARCHAR(20)
     - NO
     -
   * - country
     - CHAR(2)
     - NO
     - ISO 3166-1 alpha-2, default 'US'
   * - is_primary
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - is_verified
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - verified_at
     - DATETIME
     - YES
     -
   * - data_source
     - VARCHAR(50)
     - YES
     -
   * - is_enriched
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Indexes:**

- ``idx_ca_contact`` on ``contact_id``
- ``idx_ca_postal`` on ``postal_code``

.. _client-hub-dm-org-phones:

org_phones
======================================================================

Phone numbers for organizations. Same structure as ``contact_phones``
but references ``organization_id``.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - organization_id
     - BIGINT UNSIGNED
     - NO
     - FK → organizations.id ON DELETE CASCADE
   * - phone_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → phone_types.id
   * - phone_number
     - VARCHAR(20)
     - NO
     -
   * - phone_extension
     - VARCHAR(10)
     - YES
     -
   * - is_primary
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - data_source
     - VARCHAR(50)
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

.. _client-hub-dm-org-emails:

org_emails
======================================================================

Email addresses for organizations.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - organization_id
     - BIGINT UNSIGNED
     - NO
     - FK → organizations.id ON DELETE CASCADE
   * - email_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → email_types.id
   * - email_address
     - VARCHAR(255)
     - NO
     -
   * - is_primary
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - data_source
     - VARCHAR(50)
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

.. _client-hub-dm-org-addresses:

org_addresses
======================================================================

Physical addresses for organizations.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - organization_id
     - BIGINT UNSIGNED
     - NO
     - FK → organizations.id ON DELETE CASCADE
   * - address_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → address_types.id
   * - address_line1
     - VARCHAR(255)
     - NO
     -
   * - address_line2
     - VARCHAR(255)
     - YES
     -
   * - city
     - VARCHAR(100)
     - NO
     -
   * - state
     - VARCHAR(50)
     - NO
     -
   * - postal_code
     - VARCHAR(20)
     - NO
     -
   * - country
     - CHAR(2)
     - NO
     - Default 'US'
   * - is_primary
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - data_source
     - VARCHAR(50)
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

.. _client-hub-dm-channel-prefs:

contact_channel_prefs
======================================================================

Communication channel preferences per contact, including opt-in/out
status for compliance.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - channel_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → channel_types.id
   * - is_preferred
     - BOOLEAN
     - NO
     - DEFAULT FALSE
   * - opt_in_status
     - ENUM('opted_in','opted_out','not_set')
     - NO
     - DEFAULT 'not_set'
   * - opted_in_at
     - DATETIME
     - YES
     -
   * - opted_out_at
     - DATETIME
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Constraints:**

- UNIQUE on ``(contact_id, channel_type_id)`` — one preference row
  per contact per channel.

**Normalization:** 3NF. The opt-in/out timestamps are attributes of
this specific preference record, not of the contact or channel.

.. _client-hub-dm-marketing-sources:

contact_marketing_sources (junction)
======================================================================

Many-to-many: how a contact found the business. A contact may have
arrived through multiple channels (e.g., saw a social media ad AND
got a referral).

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - marketing_source_id
     - BIGINT UNSIGNED
     - NO
     - FK → marketing_sources.id
   * - source_detail
     - VARCHAR(255)
     - YES
     - e.g., "Google search for 'custom embroidery near me'"
   * - attributed_at
     - DATETIME
     - YES
     - When this source was attributed
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP

**Constraints:**

- UNIQUE on ``(contact_id, marketing_source_id)``

**Why a junction table:** A contact can arrive through multiple
marketing channels (saw an ad, then got a referral, then searched
Google). Each attribution is a separate fact.

.. _client-hub-dm-contact-tags:

contact_tag_map (junction)
======================================================================

Many-to-many: user-defined tags on contacts.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE, part of composite PK
   * - tag_id
     - BIGINT UNSIGNED
     - NO
     - FK → tags.id ON DELETE CASCADE, part of composite PK
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP

**Constraints:**

- PRIMARY KEY on ``(contact_id, tag_id)``

**Why a junction table:** Tags are many-to-many by nature. A contact
can have multiple tags, and a tag can apply to multiple contacts.

.. _client-hub-dm-contact-notes:

contact_notes
======================================================================

Detailed notes attached to a contact, with authorship tracking.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - note_text
     - TEXT
     - NO
     -
   * - created_by
     - VARCHAR(100)
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

.. _client-hub-dm-contact-preferences:

contact_preferences
======================================================================

Flexible key-value preferences per contact. Stores arbitrary
preferences that don't warrant their own column: preferred contact
time, language, loyalty discount, referral codes, etc.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - pref_key
     - VARCHAR(100)
     - NO
     - Machine-readable key (e.g., "preferred_contact_time")
   * - pref_value
     - TEXT
     - NO
     - Value as string
   * - data_source
     - VARCHAR(50)
     - YES
     - Which system set this preference
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Constraints:**

- UNIQUE on ``(contact_id, pref_key)`` — one value per key per contact.

.. _client-hub-dm-views:

**********************************************************************
Database Views (Data-First)
**********************************************************************

These views are available at the database level for direct SQL access.
They provide the same intelligence as the API endpoints but without
requiring the API to be running.

.. _client-hub-dm-view-last-order:

v_contact_last_order
======================================================================

Returns one row per contact with their most recent order details:
order number, date, status, total, item types, and item descriptions.

Contacts with no orders are excluded (use LEFT JOIN if you need all).

.. _client-hub-dm-view-summary:

v_contact_summary
======================================================================

Comprehensive intelligence view — one row per contact with:

- Identity: name, type, organization, enrichment status
- Marketing flags: opt-out booleans for SMS, email, phone
- Primary contact details: phone number, email address
- Order stats: total orders, lifetime value, last order date
- Communication stats: total interactions, last communication date
- Financial: outstanding balance across all invoices
- Attribution: marketing sources (comma-separated)
- Classification: tags (comma-separated)

This is the "holistic view" referenced in the project vision. Use it
for customer analysis, marketing intelligence, and integration lookups.

.. _client-hub-dm-orders:

orders
======================================================================

Orders (product-based) and bookings (service-based) in one table.
The ``order_item_type`` on the line items distinguishes products from
services/bookings.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - uuid
     - CHAR(36)
     - NO
     - UNIQUE
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id
   * - order_status_id
     - BIGINT UNSIGNED
     - NO
     - FK → order_statuses.id
   * - order_number
     - VARCHAR(50)
     - YES
     - UNIQUE, human-readable (auto-generated or manual)
   * - order_date
     - DATE
     - NO
     -
   * - due_date
     - DATE
     - YES
     - Expected completion/delivery date
   * - scheduled_at
     - DATETIME
     - YES
     - For bookings: appointment date/time
   * - subtotal
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - discount_amount
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - tax_amount
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - total
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - notes_text
     - TEXT
     - YES
     -
   * - external_refs_json
     - JSON
     - YES
     - e.g., {"invoiceninja_order_id": "..."}
   * - is_active
     - BOOLEAN
     - NO
     - DEFAULT TRUE
   * - deleted_at
     - DATETIME
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE
   * - created_by
     - VARCHAR(100)
     - YES
     -

**Indexes:**

- ``idx_orders_uuid`` on ``uuid`` (UNIQUE)
- ``idx_orders_contact`` on ``contact_id``
- ``idx_orders_status`` on ``order_status_id``
- ``idx_orders_number`` on ``order_number`` (UNIQUE)
- ``idx_orders_date`` on ``order_date``
- ``idx_orders_scheduled`` on ``scheduled_at``

**Normalization:** 3NF. ``subtotal``, ``tax_amount``, ``total`` are
stored rather than computed on-the-fly because they represent the
agreed values at order time (prices may change later). This is
standard practice in order management systems.

.. _client-hub-dm-order-items:

order_items
======================================================================

Line items within an order.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - order_id
     - BIGINT UNSIGNED
     - NO
     - FK → orders.id ON DELETE CASCADE
   * - item_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → order_item_types.id
   * - description
     - VARCHAR(500)
     - NO
     -
   * - quantity
     - DECIMAL(10,2)
     - NO
     - DEFAULT 1.00
   * - unit_price
     - DECIMAL(12,2)
     - NO
     -
   * - discount_amount
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - line_total
     - DECIMAL(12,2)
     - NO
     - (quantity * unit_price) - discount_amount
   * - sort_order
     - INT
     - NO
     - DEFAULT 0
   * - notes_text
     - TEXT
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Indexes:**

- ``idx_oi_order`` on ``order_id``

.. _client-hub-dm-order-status-history:

order_status_history
======================================================================

Audit trail of status changes on an order.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - order_id
     - BIGINT UNSIGNED
     - NO
     - FK → orders.id ON DELETE CASCADE
   * - from_status_id
     - BIGINT UNSIGNED
     - YES
     - FK → order_statuses.id (NULL for initial status)
   * - to_status_id
     - BIGINT UNSIGNED
     - NO
     - FK → order_statuses.id
   * - changed_by
     - VARCHAR(100)
     - YES
     -
   * - notes_text
     - TEXT
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP

**Indexes:**

- ``idx_osh_order`` on ``order_id``
- ``idx_osh_date`` on ``created_at``

.. _client-hub-dm-invoices:

invoices
======================================================================

Invoices linked to orders. An order can have multiple invoices
(deposit invoice, final invoice, etc.).

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - uuid
     - CHAR(36)
     - NO
     - UNIQUE
   * - order_id
     - BIGINT UNSIGNED
     - NO
     - FK → orders.id
   * - invoice_status_id
     - BIGINT UNSIGNED
     - NO
     - FK → invoice_statuses.id
   * - invoice_number
     - VARCHAR(50)
     - YES
     - UNIQUE, human-readable
   * - invoice_date
     - DATE
     - NO
     -
   * - due_date
     - DATE
     - YES
     -
   * - subtotal
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - tax_amount
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - total
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - amount_paid
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00
   * - balance_due
     - DECIMAL(12,2)
     - NO
     - DEFAULT 0.00 (total - amount_paid)
   * - external_invoice_id
     - VARCHAR(255)
     - YES
     - InvoiceNinja invoice ID
   * - notes_text
     - TEXT
     - YES
     -
   * - is_active
     - BOOLEAN
     - NO
     - DEFAULT TRUE
   * - deleted_at
     - DATETIME
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Indexes:**

- ``idx_inv_uuid`` on ``uuid`` (UNIQUE)
- ``idx_inv_order`` on ``order_id``
- ``idx_inv_number`` on ``invoice_number`` (UNIQUE)
- ``idx_inv_status`` on ``invoice_status_id``
- ``idx_inv_external`` on ``external_invoice_id``

.. _client-hub-dm-payments:

payments
======================================================================

Payment records against an invoice.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - uuid
     - CHAR(36)
     - NO
     - UNIQUE
   * - invoice_id
     - BIGINT UNSIGNED
     - NO
     - FK → invoices.id
   * - payment_method_id
     - BIGINT UNSIGNED
     - NO
     - FK → payment_methods.id
   * - amount
     - DECIMAL(12,2)
     - NO
     -
   * - payment_date
     - DATE
     - NO
     -
   * - reference_number
     - VARCHAR(255)
     - YES
     - Check number, transaction ID, etc.
   * - external_payment_id
     - VARCHAR(255)
     - YES
     - InvoiceNinja payment ID
   * - notes_text
     - TEXT
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP
   * - updated_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP ON UPDATE

**Indexes:**

- ``idx_pay_uuid`` on ``uuid`` (UNIQUE)
- ``idx_pay_invoice`` on ``invoice_id``
- ``idx_pay_date`` on ``payment_date``
- ``idx_pay_external`` on ``external_payment_id``

.. _client-hub-dm-communications:

communications
======================================================================

Log of all interactions with a contact across all channels.

.. list-table::
   :header-rows: 1
   :widths: 25 20 10 45

   * - Column
     - Type
     - Nullable
     - Notes
   * - id
     - BIGINT UNSIGNED AUTO_INCREMENT
     - NO
     - PK
   * - uuid
     - CHAR(36)
     - NO
     - UNIQUE
   * - contact_id
     - BIGINT UNSIGNED
     - NO
     - FK → contacts.id ON DELETE CASCADE
   * - channel_type_id
     - BIGINT UNSIGNED
     - NO
     - FK → channel_types.id
   * - order_id
     - BIGINT UNSIGNED
     - YES
     - FK → orders.id (optional link to related order)
   * - direction
     - ENUM('inbound','outbound')
     - NO
     -
   * - subject
     - VARCHAR(255)
     - YES
     -
   * - body
     - TEXT
     - YES
     -
   * - occurred_at
     - DATETIME
     - NO
     - When the communication happened
   * - external_message_id
     - VARCHAR(255)
     - YES
     - Chatwoot message ID, email message-ID, etc.
   * - created_by
     - VARCHAR(100)
     - YES
     -
   * - created_at
     - DATETIME
     - NO
     - DEFAULT CURRENT_TIMESTAMP

**Indexes:**

- ``idx_comm_uuid`` on ``uuid`` (UNIQUE)
- ``idx_comm_contact`` on ``contact_id``
- ``idx_comm_channel`` on ``channel_type_id``
- ``idx_comm_order`` on ``order_id``
- ``idx_comm_occurred`` on ``occurred_at``
- ``idx_comm_external`` on ``external_message_id``

.. _client-hub-dm-junction-summary:

**********************************************************************
Junction Tables Summary
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Junction Table
     - Connects
     - Reason
   * - contact_tag_map
     - contacts ↔ tags
     - A contact can have many tags; a tag applies to many contacts
   * - contact_marketing_sources
     - contacts ↔ marketing_sources
     - A contact can arrive via multiple marketing channels

.. _client-hub-dm-normalization:

**********************************************************************
Normalization Analysis
**********************************************************************

All tables satisfy Third Normal Form (3NF):

1. **1NF** — All columns contain atomic values. No repeating groups.
   Multi-valued attributes (phones, emails, addresses) are in
   separate child tables, not comma-separated in the parent.

2. **2NF** — No partial dependencies. Every non-key column depends on
   the entire primary key. The composite-PK junction table
   ``contact_tag_map`` has only ``created_at`` as a non-key column,
   which depends on the full composite key (when *this tag* was
   applied to *this contact*).

3. **3NF** — No transitive dependencies. Contact type labels are not
   stored on ``contacts``; they are retrieved via ``contact_type_id``
   → ``contact_types.label``. Phone/email/address type labels are FKs
   to lookup tables. Order status labels are FKs to
   ``order_statuses``. ``orders.total`` is NOT a transitive dependency
   — it represents the agreed-upon total at order time, not a computed
   value. Similarly, ``invoices.balance_due`` is a stored snapshot.

**Denormalization decisions (intentional, documented):**

- ``contacts.display_name`` — Optional override; can be computed from
  ``first_name + last_name`` but stored for cases where the display
  name differs (e.g., "Dr. Smith" vs "John Smith").
- ``external_refs_json`` on contacts, organizations, orders — Stores
  opaque integration IDs as JSON rather than in a separate table.
  These are only used for exact-match lookups and would gain nothing
  from being normalized into a join table.
- ``orders.subtotal/tax_amount/total`` — Point-in-time financial
  snapshots. Not computable from current line items because prices
  may change after order creation.

.. _client-hub-dm-table-count:

**********************************************************************
Complete Table List
**********************************************************************

**Entity tables (18):**

1. business_settings
2. contacts (includes marketing_opt_out_sms/email/phone flags)
3. organizations
4. contact_phones
5. contact_emails
6. contact_addresses
7. org_phones
8. org_emails
9. org_addresses
10. contact_channel_prefs
11. contact_preferences (flexible key-value per contact)
12. contact_notes
13. orders
14. order_items
15. order_status_history
16. invoices
17. payments
18. communications

**Junction tables (2):**

19. contact_tag_map
20. contact_marketing_sources

**Lookup tables (11):**

21. contact_types
22. phone_types
23. email_types
24. address_types
25. channel_types
26. marketing_sources
27. order_statuses
28. order_item_types
29. invoice_statuses
30. payment_methods
31. tags

**Views (2):**

32. v_contact_last_order — last order details per contact
33. v_contact_summary — holistic intelligence view (lifetime value,
    order stats, communication stats, opt-outs, tags, sources)

**Total: 31 tables + 2 views**
