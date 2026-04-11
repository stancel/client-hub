.. _client-hub-multi-source:

######################################################################
Client Hub — Multi-Source Architecture
######################################################################

.. _client-hub-ms-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub remains **single-tenant per company** — one company, one
database, one deployment. No customer data is ever mixed across
companies.

Within a single company's instance, however, many different
**sources** push data in. A source is any system or integration
that writes to client-hub. For a dental practice this might include:

- ``dental_care_website`` — the public Next.js site
- ``dental_care_scheduler`` — the booking flow
- ``dental_care_chatwoot`` — inbound chats and texts
- ``dental_care_cti`` — the SIP phone system integration
- ``dental_care_invoiceninja`` — billing sync

Each source has its own API key(s) so the practice can see which
system logged which event, revoke a leaked key without breaking
every other integration, and filter reports by source.

.. _client-hub-ms-terminology:

**********************************************************************
Sources vs Marketing Sources
**********************************************************************

**These are different concepts.** Do not confuse them.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Concept
     - ``sources`` table
     - ``marketing_sources`` table
   * - Question answered
     - Which **system** logged this event?
     - Where did the **lead** discover the business?
   * - Examples
     - website, cti, chatwoot, scheduler
     - google_search, referral, walk_in, social_media_ad
   * - Stamped on
     - ``contacts.first_seen_source_id``,
       ``communications.source_id``
     - ``contact_marketing_sources`` junction table
   * - Who sets it
     - Auto-stamped by API middleware from the API key
     - Manually set or inferred from UTM parameters

.. _client-hub-ms-schema:

**********************************************************************
Schema
**********************************************************************

Two new tables (migration 014):

**sources** — One row per integration that pushes data in.

- ``code`` — Machine-readable slug (e.g., ``dental_care_website``)
- ``name`` — Human display name
- ``source_type`` — Category: website, cti, chat, crm, ads,
  scheduler, other
- ``domain`` — Primary public domain if applicable

**api_keys** — Per-source API credentials.

- ``key_prefix`` — First 8 chars for admin display (never expose
  the full key in list views)
- ``key_value`` — Full key, stored as plaintext (see Security note)
- ``source_id`` — FK to sources
- ``is_active`` / ``revoked_at`` — Soft revocation

Two new columns (migration 015):

- ``contacts.first_seen_source_id`` — NOT NULL FK to sources.
  Set automatically when a contact is first created via the API.
- ``communications.source_id`` — NOT NULL FK to sources.
  Set automatically on every communication event.

.. _client-hub-ms-auth:

**********************************************************************
Authentication Model
**********************************************************************

Every API request carries an ``X-API-Key`` header. The middleware
resolves it as follows:

1. **Root key** (``CLIENTHUB_ROOT_API_KEY`` env var): full admin
   access, no source context. Can manage sources, mint keys, read
   everything.
2. **Source-scoped key** (from ``api_keys`` table): writes are
   stamped with the key's ``source_id``. Reads are NOT scoped —
   any valid key can read any contact or event. This is intentional:
   the CTI system must find contacts created by the website.
3. **Invalid/revoked key**: 401.

.. _client-hub-ms-write-stamping:

**********************************************************************
Write-Time Source Stamping
**********************************************************************

- ``POST /api/v1/contacts`` — ``first_seen_source_id`` is
  auto-stamped from the request's source context. Root key defaults
  to the bootstrap source.
- ``POST /api/v1/communications`` — ``source_id`` is auto-stamped.
- Webhook endpoints use the source key configured for that
  integration.
- **Source spoofing prevention:** a non-root key cannot override
  the ``source_id`` to a different source.

.. _client-hub-ms-read-scoping:

**********************************************************************
Read-Time Scoping
**********************************************************************

**Reads are NOT scoped by source.** Any valid source-scoped API key
can query any contact or communication in the database.

This is by design: all data in a single client-hub instance belongs
to one company. Every integration that company runs should be able
to see every contact.

.. _client-hub-ms-security:

**********************************************************************
Security Notes
**********************************************************************

**API key storage:** Keys are stored as plaintext in
``api_keys.key_value``, not hashed. Rationale: if the database is
compromised, the attacker already has all the data the keys would
protect. Hashing adds complexity without meaningful defense-in-depth
in this context. The ``key_prefix`` column allows admin tooling to
display ``abc12345...`` without exposing the full key.

**Key rotation:** Create a new key for the source, update the
integration to use it, then revoke the old key. At no point is the
source's data at risk because reads are not key-scoped.
