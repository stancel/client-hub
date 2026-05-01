.. _client-hub-sources:

######################################################################
Client Hub — Sources & API Keys
######################################################################

.. _client-hub-sources-overview:

**********************************************************************
Overview
**********************************************************************

A **source** in Client Hub is the identity of an authenticated
*integration* — the consumer Next.js website, the InvoiceNinja
webhook caller, the Chatwoot widget, a future SIP/CTI agent, an MCP
write tool. Every authenticated request belongs to exactly one
source, and every authenticated *write* attaches that source's id to
the row it produces. The audit trail "where did this contact /
communication / spam-rejection / rate-limit row come from?" is
therefore preserved at the row level forever.

Sources are stored in the ``sources`` table; their authentication
secrets are stored as one or more rows in ``api_keys``. See
``docs/data-model.rst`` (sources, api_keys sections) for column
detail.

**Important distinction.** ``sources`` answers *which integration
sent us this data*. ``marketing_sources`` answers *how the customer
first heard about the business* (Google search, social media,
referral, etc.). They are orthogonal and frequently confused because
of the shared word — they are not the same dimension.

.. _client-hub-sources-discipline:

**********************************************************************
The Source-Discipline Rule
**********************************************************************

**Every consumer integration must have its own named ``sources``
row and at least one ``api_keys`` row attached to that source. The
seeded ``bootstrap`` row must never be used as a runtime
identity.**

Why:

1. **Auditability.** Every contact, communication, spam event,
   rate-limit row, and api_key carries the source id of the writer.
   When ``bootstrap`` is the writer, the audit log says "the install
   did this" — which is meaningless after day one.

2. **Per-integration scoping.** Future per-source rate-limit
   thresholds, per-source spam-pattern overrides, per-source
   admin dashboards, and per-source key rotation all key off the
   ``source_id``. Multiple integrations sharing the ``bootstrap``
   row are indistinguishable to those features.

3. **Safer key rotation.** Keys are rotated by issuing a new
   ``api_keys`` row attached to the same source, deploying the new
   value, then revoking the old row. If five integrations share
   one bootstrap source, you can't rotate one of them without
   coordinating with the other four.

4. **Cleaner offboarding.** A consumer site decommissioning is
   ``UPDATE sources SET is_active=FALSE WHERE id=…`` — it tombstones
   the integration without deleting the audit history it produced.
   That only works if the source is uniquely associated with that
   integration.

5. **Fleet readiness.** A future control-plane Client Hub will read
   ``sources`` across instances to render "which businesses run
   which integrations." Bootstrap-as-runtime breaks that
   visualization.

.. _client-hub-sources-bootstrap:

**********************************************************************
The ``bootstrap`` Row
**********************************************************************

Migration 014 seeds a single row with ``code='bootstrap'``,
``name='Bootstrap Source'``, ``source_type='other'``, and a
description that reads:

   *"Initial source created by the installer. Rename or create
   additional sources as needed."*

That row exists so the very first authenticated request to a
freshly-installed instance has a place to attach to. The installer
is then expected to either:

- **Single-tenant case** — rename the bootstrap row in place to the
  consumer site's identity (``code``, ``name``, ``source_type``,
  ``domain``). The row's ``id`` stays the same, all FKs survive,
  and the rename is a single ``UPDATE``. See
  ``scripts/rename-bootstrap-source.sql`` for the parameterized
  template; CDC and Clever Orchid have committed
  per-VPS rename files in ``scripts/`` for audit.

- **Multi-tenant / multi-source case** — leave the bootstrap row in
  place and create one or more properly-named source rows
  alongside it via ``POST /api/v1/admin/sources`` (or the
  installer's ``--first-source-*`` flags). The bootstrap row will
  end up with **zero inbound FK references** and is then dropped
  by migration 029 the next time the install runs migrations.

Either way, ``bootstrap`` is never the live runtime identity of a
real integration.

.. _client-hub-sources-installer:

**********************************************************************
What the Installer Does (v0.3.3+)
**********************************************************************

``scripts/install.sh`` enforces source discipline at install time:

- ``--first-source-code`` is **required** and rejects ``bootstrap``.
  An install that doesn't supply a code (or that explicitly tries
  to set the code to ``bootstrap``) fails with a pointed error.
- ``--first-source-name``, ``--first-source-domain``, and
  ``--first-source-type`` round out the row. Domain is plumbed in
  at create time so the marketing-source derivation can use it
  authoritatively.
- The install-generated API key is attached to that named source,
  not to ``bootstrap``. The bootstrap row is left untouched and
  remains orphan-eligible for migration 029.

Two production VPSes pre-date this enforcement:

- **Complete Dental Care** (CDC) — installed correctly with
  ``complete_dental_care_website`` as a separate source. The
  vestigial ``bootstrap`` row was dropped by migration 029
  (v0.3.2).
- **Clever Orchid** (CO) — installed with no named source; every
  contact / communication / api_key was attributed to
  ``bootstrap``. The row was renamed in place to
  ``clever_orchid_website`` via
  ``scripts/rename-bootstrap-clever-orchid.sql`` (v0.3.2).
  Because the rename was in-place, all 15 contacts and the api_key
  continued to resolve through the same FK.

.. _client-hub-sources-rotation:

**********************************************************************
Key Rotation
**********************************************************************

When a consumer site's API key needs to rotate (suspected leak,
scheduled rotation, employee turnover):

1. **Issue a new key** for the same source via
   ``POST /api/v1/admin/sources/{uuid}/api-keys`` with a
   descriptive ``name`` (e.g. ``"Rotated 2026-08-01"``).
2. **Deploy** the new key to the consumer site's ``.env`` and
   redeploy.
3. **Verify** the consumer site is using the new key by checking
   ``api_keys.last_used_at`` for the new row.
4. **Revoke** the old key by setting ``revoked_at`` on its row
   (``PUT /api/v1/admin/sources/{uuid}/api-keys/{key_uuid}`` with
   ``is_active=false``).

All historical attribution remains intact because rows are
attributed by ``source_id``, not ``api_key_id``. The rotated key
is offboarded; the source identity persists.

.. _client-hub-sources-multi-source:

**********************************************************************
Multi-Source Installs
**********************************************************************

A single Client Hub instance can serve many integrations. Each gets
its own source row + api_key. Examples:

- ``my_business_website`` (``website``) — the consumer Next.js
  site
- ``my_business_chatwoot`` (``webhook``) — Chatwoot calling the
  ``/webhooks/chatwoot`` endpoint
- ``my_business_invoiceninja`` (``webhook``) — InvoiceNinja calling
  ``/webhooks/invoiceninja``
- ``my_business_sip_cti`` (``other``) — the SIP/CTI agent doing
  caller lookups
- ``my_business_internal_mcp`` (``mcp``) — an internal MCP write
  tool used by ops

All of them attach their writes to their own ``source_id``, so the
admin events feed (``GET /api/v1/admin/events``) and the
``v_events_by_source`` view can filter by ``source_code`` to show
"everything Chatwoot logged this week" or "everything the website
captured today."

.. _client-hub-sources-references:

**********************************************************************
References
**********************************************************************

- ``api/app/models/source.py`` — Source ORM
- ``api/app/models/api_key.py`` — ApiKey ORM
- ``api/app/middleware/auth.py`` — request-time source resolution
- ``migrations/014_sources_and_api_keys.sql`` — schema
- ``migrations/028_sources_domain_backfill.sql`` — domain backfill
- ``migrations/029_drop_orphaned_bootstrap_source.sql`` — orphan
  cleanup
- ``scripts/rename-bootstrap-source.sql`` — parameterized
  in-place rename template
- ``docs/data-model.rst`` — column-level table documentation
- ``docs/Multi-Source.rst`` — broader multi-source design memo
