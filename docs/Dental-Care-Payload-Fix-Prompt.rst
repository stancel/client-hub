.. _dental-care-payload-fix-prompt:

######################################################################
Complete Dental Care — Client-Hub Payload Fix Prompt
######################################################################

:Target audience: Claude Code session opened in
                  ``~/Sites/complete-dental-care-nextjs/``
:Created: 2026-04-11 (after client-hub external_refs_json fix)
:Severity: **Medium** — events land in client-hub but with thin
           metadata; booking.cancelled overwrites booking.created
:Scope: Narrow — fix ``lib/client-hub.ts`` payload enrichment and
        scheduler hook wiring. No client-hub changes — the API
        side is already correct.
:Companion: ``~/docker/client-hub/docs/Cross-Project-Integration.rst``
            (see the "external_refs_json Payload Contract" section)


.. contents:: Table of Contents
   :local:
   :depth: 2


**********************************************************************
How to use this document
**********************************************************************

Open this file in a fresh Claude Code session rooted at
``~/Sites/complete-dental-care-nextjs/``. Read it in full, use
``TaskCreate`` to track progress, execute, verify with a live
booking round-trip, commit, push.

This is a **narrow** prompt. It fixes two specific issues discovered
during the client-hub external_refs_json deployment on 2026-04-11.
Do not expand scope into unrelated cleanup.


**********************************************************************
Context
**********************************************************************

On 2026-04-11, ``client-hub`` shipped a fix for a Pydantic schema
gap that was silently dropping ``external_refs_json`` on every
contact create. See
``~/docker/client-hub/docs/External-Refs-Json-Fix-Prompt.rst`` and
commit ``fa6bf2d`` in ``stancel/client-hub``.

After the fix was deployed to the production VPS
(``client-hub-complete-dental-care.onlinesalessystems.com``), Brad
submitted a real booking on
``https://completedentalcarecolumbia.com/book`` and cancelled it
to verify the round-trip.

**The good news:** ``external_refs_json`` is no longer NULL. The
server-side fix works end-to-end — the POST body is now persisted
and reads back correctly via ``JSON_EXTRACT``.

**The bad news:** the payload this site is sending is thin and is
being clobbered on cancellation. The actual JSON stored on the
contact row after booking + cancel was::

    {
      "source_page": "/book",
      "site_source_code": "complete_dental_care_website",
      "extra": {
        "scheduler_event": "booking.cancelled",
        "appointment_id": 6,
        "service_name": "Filling"
      }
    }

Missing (but expected per the payload contract in
``Cross-Project-Integration.rst``):

- ``referrer``
- ``ip_address``
- ``user_agent``
- ``gtm_client_id``
- ``utm`` parameters
- ``extra.staff_name``
- ``extra.start_date``
- ``extra.total_price``

And the fact that the stored payload has
``scheduler_event: "booking.cancelled"`` means the cancellation
handler **overwrote** the ``booking.created`` payload that had
already been written seconds earlier. The created hook's richer
metadata was lost.


**********************************************************************
Issue 1 — lib/client-hub.ts is not collecting request headers
**********************************************************************

Expected behavior: every server-side call into client-hub should
include ``user_agent``, ``ip_address``, and ``referrer`` read from
``next/headers`` (or the request object) at the point of the
hook registration in ``lib/scheduler-init.ts``.

Actual behavior: the booking hook calls
``logConversionBackground(...)`` with only ``sourcePage`` and a
partial ``extra`` object.

.. rubric:: Fix

1. Open ``lib/scheduler-init.ts`` and find the
   ``registerHook('booking.created', ...)`` and
   ``registerHook('booking.cancelled', ...)`` handlers.
2. On each handler, **read request headers at hook-registration
   time is impossible** — the hook fires from a server action,
   not a request context. Instead, the scheduler's hook payload
   needs to carry the headers **captured at the point the user
   clicked submit on the booking form**.
3. Modify the booking form's server action (check
   ``app/book/**`` or wherever the form posts) to capture
   ``headers()`` at form-submit time and pass them through into
   the scheduler call, so the scheduler's hook payload can
   forward them into ``external_refs_json``.
4. If the ``@bradstancel/website-scheduler`` package does not
   currently accept extra metadata on the ``createAppointment``
   call, either:

   - Extend the scheduler package to carry a freeform
     ``clientMetadata`` field through to its hooks, OR
   - Stash the request headers in the scheduler appointment's
     own ``notes`` / ``metadata`` column and read them back in
     the hook handler.

.. rubric:: Fields to collect

From ``headers()`` in the booking form server action::

    import { headers } from "next/headers";

    const h = await headers();
    const requestMeta = {
      user_agent: h.get("user-agent") ?? undefined,
      ip_address:
        h.get("x-forwarded-for")?.split(",")[0].trim() ??
        h.get("x-real-ip") ??
        undefined,
      referrer: h.get("referer") ?? undefined,
    };

From the form's landing URL (client-side, persisted to session
before submit) or from ``searchParams``::

    const utm = {
      source:   searchParams.get("utm_source")   ?? undefined,
      medium:   searchParams.get("utm_medium")   ?? undefined,
      campaign: searchParams.get("utm_campaign") ?? undefined,
      term:     searchParams.get("utm_term")     ?? undefined,
      content:  searchParams.get("utm_content")  ?? undefined,
    };

From the scheduler appointment object (already available inside
the hook handler — verify against the actual hook payload shape
in ``@bradstancel/website-scheduler``)::

    extra: {
      scheduler_event: "booking.created",   // or "booking.cancelled"
      appointment_id: appointment.id,
      service_name: appointment.serviceName,
      staff_name: appointment.staffName,
      start_date: appointment.startDate,
      total_price: appointment.totalPrice,
    }


**********************************************************************
Issue 2 — booking.cancelled is overwriting booking.created
**********************************************************************

The current dental care handler for ``booking.cancelled`` calls
``logConversionBackground(...)`` which POSTs to
``/api/v1/contacts`` with the same email — client-hub upserts on
email and replaces ``external_refs_json`` with whatever the latest
POST sends. Result: the cancellation handler's thinner payload
clobbers the richer one the create handler just wrote.

.. rubric:: Fix

Follow the pattern documented in
``~/docker/client-hub/docs/Cross-Project-Integration.rst`` under
"Don't shadow — merge":

**Option A (preferred):** the cancellation hook should NOT
re-upsert the contact. It should just append a communication row
via ``POST /api/v1/communications`` with
``channel_code = booking_cancelled``, referencing the existing
contact by UUID or by email lookup. Leave the contact's
``external_refs_json`` alone.

The contact was already created by the ``booking.created`` hook
seconds earlier; look it up via
``GET /api/v1/lookup/email/{email}`` to get the UUID, then post
the communication.

**Option B (fallback):** if you really must update the contact on
cancel (e.g. to stamp a ``cancelled_at`` field), GET the current
``external_refs_json``, deep-merge the new fields on top, and
``PUT /api/v1/contacts/{uuid}``. Never replace.

Check whether ``lib/client-hub.ts`` has a helper for appending a
communication without re-upserting the contact. If not, add one::

    export async function logCommunication(input: {
      contactUuid?: string;
      email?: string;
      channel: ConversionEvent;
      subject?: string;
      body?: string;
      externalRefs?: Record<string, unknown>;
    }): Promise<void> { ... }


**********************************************************************
Issue 3 — frontdesk cancellation email not firing (separate bug)
**********************************************************************

When Brad cancelled the test appointment from
``/admin/scheduler/appointments``, the Google Calendar entry was
removed but ``frontdesk@completedentalcarecolumbia.com`` did not
receive a cancellation notification email. The booking-created
email had fired correctly.

This is a **separate** notification wiring bug in either:

- ``@bradstancel/website-scheduler`` — the ``booking.cancelled``
  hook in ``src/notifications/sender.ts`` may not be registering
  the email notifier, OR
- ``lib/scheduler-init.ts`` — the email notifier may only be
  registered for ``booking.created``, not ``booking.cancelled``

Investigate after Issues 1 and 2 are shipped. If it turns out to
be a bug in the scheduler package, open an issue against
``@bradstancel/website-scheduler`` rather than patching around it
in the dental care site.


**********************************************************************
Success criteria
**********************************************************************

Done when:

- [ ] ``lib/client-hub.ts`` (or the booking form server action
  that calls it) captures ``user_agent``, ``ip_address``,
  ``referrer``, and UTM parameters and passes them through to
  ``external_refs_json``
- [ ] Scheduler booking hooks populate ``extra`` with
  ``scheduler_event``, ``appointment_id``, ``service_name``,
  ``staff_name``, ``start_date``, ``total_price``
- [ ] ``booking.cancelled`` hook does NOT re-upsert the contact;
  it appends a communication row instead (or deep-merges if
  update is truly required)
- [ ] Issue 3 investigated and either fixed or filed as a
  separate issue against the scheduler package
- [ ] Round-trip smoke test: submit a booking with a
  plus-addressed email, cancel it, then on the VPS run::

      ssh root@client-hub-complete-dental-care.onlinesalessystems.com \\
        "docker exec clienthub-mariadb mariadb -u root \\
         -p\\$(grep MARIADB_ROOT_PASSWORD /opt/client-hub/.env | cut -d= -f2) \\
         clienthub -e 'SELECT external_refs_json FROM contacts \\
         WHERE last_name LIKE \"stancel%\" \\
         ORDER BY created_at DESC LIMIT 1\\\\G'"

  Expect every field from the payload contract populated, and
  expect the richer ``booking.created`` metadata to survive the
  cancellation.


**********************************************************************
Non-goals
**********************************************************************

- Any changes to ``~/docker/client-hub/`` — the server-side fix is
  already deployed (commit ``fa6bf2d``)
- Any changes to other Web Factory sites — Clever Orchid will get
  the correct pattern from day one via the checklist in
  ``Cross-Project-Integration.rst``
- Any refactoring of ``@bradstancel/website-scheduler`` beyond
  the minimum needed to carry request metadata through to hooks
- Adding new ``channel_types`` codes beyond what the integration
  guide already defines


**********************************************************************
References
**********************************************************************

- Client Hub fix that unblocked this work:
  ``~/docker/client-hub/docs/External-Refs-Json-Fix-Prompt.rst``
- Payload contract and checklist for new sites:
  ``~/docker/client-hub/docs/Cross-Project-Integration.rst``
  (see "external_refs_json Payload Contract" section)
- Scheduler package:
  ``@bradstancel/website-scheduler`` (check
  ``src/notifications/sender.ts`` for hook fire points)
- Reference scheduler init:
  ``~/Sites/complete-dental-care-nextjs/lib/scheduler-init.ts``
- Reference client-hub caller:
  ``~/Sites/complete-dental-care-nextjs/lib/client-hub.ts``
- Live client-hub instance:
  ``https://client-hub-complete-dental-care.onlinesalessystems.com``
