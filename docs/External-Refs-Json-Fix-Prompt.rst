.. _external-refs-json-fix-prompt:

######################################################################
Client Hub — external_refs_json Data-Loss Bug Fix Prompt
######################################################################

:Target audience: Claude Code session opened in ``~/docker/client-hub/``
:Created: 2026-04-11 (after the initial Post-Deployment-Fixes session)
:Severity: **High** — silent data loss on every contact creation
:Scope: Narrow — one bug, no cleanup work, no installer changes
:Companion: ``docs/Post-Deployment-Fixes-Prompt.rst`` (already run
            in a prior session — do NOT redo its work)


.. contents:: Table of Contents
   :local:
   :depth: 2


**********************************************************************
How to use this document
**********************************************************************

This is a **narrow, focused** follow-up prompt. It addresses exactly
one bug that was discovered AFTER the
``Post-Deployment-Fixes-Prompt.rst`` was handed off to a previous
Claude Code session.

The previous session already executed the Post-Deployment-Fixes
prompt — it cleaned up test data, fixed the installer bugs,
restructured seed data handling, and hardened the installer. **Do
not redo any of that work.** This prompt is only about the
``external_refs_json`` schema gap described below.

Read in full, use ``TaskCreate`` to track progress, execute, verify,
commit, push.


**********************************************************************
Context
**********************************************************************

On 2026-04-11, after the initial client-hub deployment to
``client-hub-complete-dental-care.onlinesalessystems.com`` and the
wiring of the first consumer (``complete-dental-care-nextjs``), an
end-to-end test was run:

1. Brad submitted a real booking on
   ``https://completedentalcarecolumbia.com/book``
2. The ``@bradstancel/website-scheduler`` package fired its
   ``booking.created`` hook at ``src/notifications/sender.ts:73``
3. The dental care site's ``lib/scheduler-init.ts`` had registered
   a handler via ``registerHook('booking.created', ...)`` that
   called ``logConversionBackground(...)`` from ``lib/client-hub.ts``
4. ``lib/client-hub.ts`` POSTed a contact to
   ``/api/v1/contacts`` with a full payload including
   ``external_refs_json``
5. Client Hub correctly persisted the contact row, the
   communication row, and auto-stamped
   ``first_seen_source_id = complete_dental_care_website``

Then Brad cancelled the booking from
``/admin/scheduler/appointments``, which fired
``fireHook('booking.cancelled', ...)`` (sender.ts:258–262) and
client-hub correctly received and persisted a
``channel_code = booking_cancelled`` communication row.

**Both events are correctly logged in client-hub.** Source
stamping works. Channel codes work. Timestamps are correct. The
whole pipeline is green.

**But when we queried the contact's ``external_refs_json`` column,
it was NULL** — despite the POST body having included a rich
nested object with IP address, user agent, referrer, UTM
parameters, and the entire scheduler payload (appointment_id,
service_name, staff_name, start_date, total_price, etc.).

This data-loss is silent. The client side has no way to know it's
happening — the API returns 201 Created with the new contact UUID,
and there's no error response indicating the ``external_refs_json``
was dropped.


**********************************************************************
Root cause
**********************************************************************

Verified by direct grep on 2026-04-11::

    grep -rn "external_refs_json" /home/brad/docker/client-hub/api/app/

Results:

- ``api/app/models/contact.py:30`` — column exists on ORM model::

    external_refs_json: Mapped[str | None] = mapped_column(Text)

- ``api/app/models/organization.py:18`` — same column on Organization
- ``api/app/models/order.py:26`` — same column on Order
- ``api/app/routers/webhooks.py:56`` — only read-usage (LIKE query
  for InvoiceNinja webhook lookups)

**Zero references in ``api/app/schemas/``.** The Pydantic
request/response models for Contact, Organization, and Order do
not declare ``external_refs_json`` as a field.

FastAPI + Pydantic's default behavior is to **silently ignore
unknown fields** in request bodies. That means every POST body that
includes ``external_refs_json`` has been having that field stripped
at the Pydantic layer before it ever reaches the create service or
the ORM — regardless of whether the client sent it correctly.

Result: ``contacts.external_refs_json`` (and presumably
``organizations.external_refs_json``, ``orders.external_refs_json``)
is NULL for every row ever created through the API.


**********************************************************************
Impact
**********************************************************************

.. rubric:: On production data

- Every existing contact created via ``POST /api/v1/contacts`` has
  ``external_refs_json = NULL``. Historical data is unrecoverable
  — the API never persisted it. Cleanup will wipe these anyway
  (the previous session's Section 3 cleanup handled test data;
  any real customer contacts will need to be re-enriched by
  future form submissions once the fix ships).

.. rubric:: On the dental care integration

- ``lib/client-hub.ts`` in ``~/Sites/complete-dental-care-nextjs/``
  is already sending the full payload. It needs **zero** changes.
  Once the fix ships on the API side, the very next form submit
  or booking will persist the rich metadata automatically.

.. rubric:: On future integrations

- Every Web Factory site that integrates via the standard
  ``lib/client-hub.ts`` pattern will be hit by this bug. Fixing
  it now prevents a wave of silent data loss as more sites come
  online.

.. rubric:: On the Patterson Eaglesoft integration Brad is planning

- When the Eaglesoft → client-hub sync is built, the natural
  place to stash things like the Eaglesoft patient ID, chart
  number, last-visit date, balance, etc. is
  ``external_refs_json``. Shipping this fix before that
  integration is essential — otherwise every Eaglesoft sync would
  silently drop the Eaglesoft-specific metadata.


**********************************************************************
The fix
**********************************************************************

Step 1 — Update the Contact Pydantic schemas
======================================================================

File: ``api/app/schemas/contact.py`` (or wherever the contact
Pydantic models live — check ``api/app/schemas/__init__.py`` for
the layout).

Add ``external_refs_json`` as an optional field to:

- ``ContactCreate`` (or equivalent for ``POST /api/v1/contacts``)
- ``ContactUpdate`` (or equivalent for ``PUT /api/v1/contacts/{uuid}``)

Recommended type::

    from typing import Any
    external_refs_json: dict[str, Any] | None = None

Use ``dict[str, Any]`` rather than a stricter shape so that
integrations can attach arbitrary metadata without needing a schema
change in client-hub every time. The convention for what goes in
there is documented in
``docs/Cross-Project-Integration.rst``, but the enforcement
happens at the application layer, not the Pydantic layer — that's
intentional flexibility.

Also add it to the ``ContactResponse`` / ``ContactSummary`` / any
read model that currently returns contacts, so clients can read
it back after creating or updating.

Step 2 — Serialize dict → JSON string in the create service
======================================================================

The ORM column is ``Text``, not ``JSON`` (verified at
``api/app/models/contact.py:30``). That means the create service
has to serialize the dict to a JSON string before assignment::

    import json

    contact_model.external_refs_json = (
        json.dumps(payload.external_refs_json)
        if payload.external_refs_json is not None
        else None
    )

And deserialize on read so the API returns a proper dict/object,
not a string::

    import json

    response_external_refs = (
        json.loads(contact.external_refs_json)
        if contact.external_refs_json
        else None
    )

Keep the JSON parsing defensive — wrap in try/except and return
``None`` on parse failure so a malformed historical row doesn't
500 the response. Log a warning.

Step 3 — Same fix for Organization and Order
======================================================================

The ``external_refs_json`` column exists on three models:

- ``Contact`` (primary — most important)
- ``Organization``
- ``Order``

Check whether ``OrganizationCreate``, ``OrganizationUpdate``,
``OrderCreate``, and ``OrderUpdate`` Pydantic schemas also omit
the field. If they do, apply the same fix to them. If any of those
create/update endpoints don't exist yet, skip those — only patch
where there's an actual bug.

Step 4 — Tests
======================================================================

Add tests in ``api/tests/test_contacts.py``:

1. ``test_create_contact_with_external_refs_json`` — POST a contact
   with a rich ``external_refs_json`` payload, assert the response
   echoes it back, then verify via DB query that it persists.

2. ``test_create_contact_without_external_refs_json`` — POST a
   contact without that field, assert it's NULL in the DB and
   ``None`` in the response. Make sure backwards compatibility is
   preserved (callers that don't send it shouldn't break).

3. ``test_update_contact_external_refs_json`` — PUT a contact to
   replace its ``external_refs_json``, assert the new value
   sticks.

4. ``test_create_contact_external_refs_json_deep_nested`` — POST
   with a deeply nested structure (match the shape from
   ``lib/client-hub.ts``'s actual payload: top-level keys like
   ``source_page``, ``ip_address``, ``user_agent``, and a nested
   ``extra`` object with 5+ keys inside it). Verify round-trip
   integrity.

Repeat equivalent tests for Organization and Order if you fixed
those too.

Step 5 — Round-trip verification against the dental care integration
======================================================================

After the fix ships and the VPS is updated:

1. ``ssh`` to
   ``client-hub-complete-dental-care.onlinesalessystems.com``
2. ``cd /opt/client-hub && git pull && docker compose -f docker-compose.bundled.yml build client-hub-api && docker compose -f docker-compose.bundled.yml up -d``
3. Submit a test booking on
   ``https://completedentalcarecolumbia.com/book`` using a plus-
   addressed gmail like ``brad.stancel+fix-test-20260411@gmail.com``
4. Cancel it immediately from ``/admin/scheduler/appointments``
5. Query::

     SELECT
       first_name,
       last_name,
       JSON_EXTRACT(external_refs_json, '$.extra.service_name') AS service,
       JSON_EXTRACT(external_refs_json, '$.extra.staff_name')   AS staff,
       JSON_EXTRACT(external_refs_json, '$.extra.start_date')   AS start_date,
       JSON_EXTRACT(external_refs_json, '$.ip_address')         AS ip,
       JSON_EXTRACT(external_refs_json, '$.user_agent')         AS ua
     FROM contacts
     WHERE last_name LIKE 'stancel%'
     ORDER BY created_at DESC
     LIMIT 1;

   Expect every column populated (not NULL). That confirms the
   full round-trip: scheduler hook → dental care Next.js site →
   client-hub API → Pydantic schema → ORM → Text column →
   ``JSON_EXTRACT`` read path.


**********************************************************************
Optional but recommended — migrate the column type Text → JSON
**********************************************************************

MariaDB 12 has native JSON support. The current column type is
``Text``, which works but requires application-level
serialization and loses the benefit of ``JSON_EXTRACT`` /
``JSON_SET`` / ``JSON_CONTAINS`` being able to use indexed lookups.

Consider adding a new migration::

    migrations/019_contacts_external_refs_json_type.sql

That alters the three columns::

    ALTER TABLE contacts      MODIFY COLUMN external_refs_json JSON NULL;
    ALTER TABLE organizations MODIFY COLUMN external_refs_json JSON NULL;
    ALTER TABLE orders        MODIFY COLUMN external_refs_json JSON NULL;

MariaDB 12's ``JSON`` type is actually ``LONGTEXT`` with a CHECK
constraint on the client side, so existing rows continue to work
as long as they either contain valid JSON or are NULL. Verify no
existing rows have a malformed value first::

    SELECT COUNT(*)
    FROM contacts
    WHERE external_refs_json IS NOT NULL
      AND JSON_VALID(external_refs_json) = 0;

Should return 0 (since all current values are NULL anyway post
the Post-Deployment-Fixes cleanup).

If you do this migration, also update the ORM model type hint
from ``str | None`` to something like ``dict[str, Any] | None``
and remove the serialization boilerplate from Step 2 — SQLAlchemy
will handle JSON serialization automatically.

**This optional step is nice-to-have, not a blocker.** Ship Step
1–4 first, let it run for a day, then decide whether the column
type change is worth the extra work.


**********************************************************************
Non-goals
**********************************************************************

Explicitly out of scope for this prompt:

- Any installer changes (``install.sh``, ``docker-compose.bundled.yml``,
  ``scripts/bootstrap-migrations.sh``) — the previous prompt
  handled those
- Any seed data handling changes — previous prompt handled those
- Any test data cleanup — previous prompt handled those
- Any smoke test fixes beyond the ``external_refs_json`` test
  additions in Step 4
- Changes to ``lib/client-hub.ts`` in the dental care repo — it's
  already correct; this bug is entirely server-side
- Adding new API endpoints beyond the existing CRUD
- Schema changes to any other model


**********************************************************************
Success criteria
**********************************************************************

Done when:

- [ ] ``ContactCreate`` Pydantic schema declares
  ``external_refs_json: dict[str, Any] | None = None``
- [ ] ``ContactUpdate`` does the same
- [ ] ``ContactResponse`` (or equivalent read model) returns the
  field as a proper dict, not a JSON string
- [ ] The create service serializes dict → JSON string before
  assigning to the ORM column (or, if you did the optional Text
  → JSON migration, relies on SQLAlchemy to handle it)
- [ ] Same fix applied to Organization and Order where
  applicable
- [ ] New tests in ``api/tests/test_contacts.py`` cover all four
  cases (with, without, update, deep nested)
- [ ] ``pytest api/tests/ -v`` passes (was 78 before this; should
  be 78 + however many new tests you add)
- [ ] ``ruff check`` and ``rstcheck`` clean
- [ ] CI green on the new branch
- [ ] Round-trip verification from Step 5 confirmed on the live
  VPS after ``git pull`` + rebuild
- [ ] ``CHANGELOG.rst`` updated with the fix
- [ ] Optional: ``migrations/019_*_json_type.sql`` shipped if you
  chose to do the column type change


**********************************************************************
References
**********************************************************************

- Previous prompt (already run):
  ``~/docker/client-hub/docs/Post-Deployment-Fixes-Prompt.rst``
- Original install prompt:
  ``~/docker/client-hub/docs/Installation-Implementation-Prompt.rst``
- Dental care integration caller:
  ``~/Sites/complete-dental-care-nextjs/lib/client-hub.ts``
- Dental care scheduler hook wiring:
  ``~/Sites/complete-dental-care-nextjs/lib/scheduler-init.ts``
- Live production instance:
  ``https://client-hub-complete-dental-care.onlinesalessystems.com``
