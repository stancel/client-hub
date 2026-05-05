.. _client-hub-cross-project:

######################################################################
Client Hub — Cross-Project Integration Guide
######################################################################

.. _client-hub-cp-overview:

**********************************************************************
Overview
**********************************************************************

This guide explains how to integrate any Next.js "Web Factory" site
with Client Hub. The integration is designed to be copy-paste
portable — install the SDK package, set three env vars, drop in
the reference module, and start pushing events.

The canonical integration path is the **published TypeScript SDK**:
``@bradstancel/clienthub-sdk`` on the private npm registry at
``https://npm.onlinesalessystems.com/`` — same registry every
Web Factory site already uses for ``@bradstancel/website-scheduler``.
Both production consumer sites (Complete Dental Care and Clever
Orchid) are on this pattern as of v0.3.5 (2026-05-05). The hand-rolled
``fetch()`` pattern that earlier versions of this guide recommended
is **deprecated** — new sites should always start from the SDK; sites
still on the old pattern should migrate (see CDC's commit ``0b46c9e``
or Clever Orchid's ``6524034`` for worked examples in the
consumer-site repos).

.. _client-hub-cp-env-vars:

**********************************************************************
Environment Variables
**********************************************************************

Add to your Next.js site's ``.env.local``:

.. code-block:: text

   CLIENTHUB_URL=https://client-hub.example.com
   CLIENTHUB_API_KEY=your_source_scoped_api_key_here
   CLIENTHUB_SOURCE_CODE=my_website
   NPM_TOKEN=<consumer-token>          # for `npm install` only

The first three are runtime env vars consumed by ``lib/client-hub.ts``
at request time. ``NPM_TOKEN`` is **install-time only** — it lets
``npm install`` resolve packages from the private registry. It does
not need to be present in the runtime environment of the Next.js
server.

.. _client-hub-cp-install:

**********************************************************************
Installing the SDK
**********************************************************************

Configure your project's ``.npmrc`` once (the same file that already
authorizes ``@bradstancel/website-scheduler``):

.. code-block:: text

   @bradstancel:registry=https://npm.onlinesalessystems.com/
   //npm.onlinesalessystems.com/:_authToken=${NPM_TOKEN}

Set ``NPM_TOKEN`` to the read-only ``consumer`` token (per
``~/docker/verdaccio/CLAUDE.md``'s scope policy — the publisher
``brad`` token is only used by the Client Hub repo's CI publish
workflow, never by consumer sites). Then:

.. code-block:: bash

   npm install @bradstancel/clienthub-sdk@^0.3.5

The ``^0.3.5`` range pulls the latest 0.3.x patch on every fresh
``npm install`` / ``npm ci``; major-version bumps (0.4.x and beyond)
are opt-in and require an explicit version change in
``package.json``. Every Client Hub release publishes the matching
SDK version automatically via the tag-triggered
``.github/workflows/publish-sdk.yml`` workflow in the Client Hub
repo.

.. _client-hub-cp-event-codes:

**********************************************************************
Standardized Event Codes
**********************************************************************

Every Web Factory site uses these canonical ``channel_types`` codes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Code
     - When to fire
   * - ``web_form``
     - Contact form submitted
   * - ``appointment_request``
     - Appointment request submitted (pre-scheduler)
   * - ``booking_started``
     - User started the booking flow
   * - ``booking_completed``
     - Booking confirmed end-to-end
   * - ``booking_cancelled``
     - Booking cancelled
   * - ``phone_click``
     - User clicked a ``tel:`` link
   * - ``book_click``
     - User clicked a booking CTA
   * - ``form_submit``
     - Generic form (fallback)
   * - ``scroll_depth``
     - Scrolled past 50/75/90% milestone
   * - ``page_view``
     - High-intent page view

.. _client-hub-cp-reference-module:

**********************************************************************
Reference Module: lib/client-hub.ts (SDK-based)
**********************************************************************

Drop this file into your Next.js project at ``lib/client-hub.ts``.
Modeled on the actual production cutover at CDC (commit ``0b46c9e``)
and Clever Orchid (commit ``6524034``). The public surface
(``logConversion``, ``logConversionBackground``,
``appendCommunication``, ``appendCommunicationBackground``,
``ConversionEvent``, ``LogConversionInput``,
``AppendCommunicationInput``) is the same as the legacy
hand-rolled module so call sites do not change when migrating.

.. code-block:: typescript

   // lib/client-hub.ts
   // Send conversion events to Client Hub via @bradstancel/clienthub-sdk.
   // Error-swallowing — never crashes caller.

   import {
     Configuration,
     ContactsApi,
     CommunicationsApi,
     LookupApi,
     ResponseError,
   } from "@bradstancel/clienthub-sdk";

   const TIMEOUT_MS = 3000;

   const config = new Configuration({
     basePath: process.env.CLIENTHUB_URL ?? "https://client-hub.example.com",
     // Function form so the env var is read on every request, not at
     // module-load time. Important for Next.js dev/HMR and edge cases.
     apiKey: () => process.env.CLIENTHUB_API_KEY ?? "",
   });

   const contacts = new ContactsApi(config);
   const communications = new CommunicationsApi(config);
   const lookups = new LookupApi(config);

   export type ConversionEvent =
     | "web_form"
     | "appointment_request"
     | "booking_started"
     | "booking_completed"
     | "booking_cancelled"
     | "phone_click"
     | "book_click"
     | "form_submit"
     | "scroll_depth"
     | "page_view";

   export interface LogConversionInput {
     event: ConversionEvent;
     email?: string;
     phone?: string;
     firstName?: string;
     lastName?: string;
     subject?: string;
     body?: string;
     sourcePage?: string;
     siteSourceCode?: string;
     referrer?: string;
     userAgent?: string;
     ipAddress?: string;
     gtmClientId?: string;
     utm?: {
       source?: string;
       medium?: string;
       campaign?: string;
       term?: string;
       content?: string;
     };
     extra?: Record<string, unknown>;
   }

   export interface AppendCommunicationInput {
     event: ConversionEvent;
     email: string; // required — used to look up the existing contact
     subject?: string;
     body?: string;
   }

   function withTimeout<T>(fn: (signal: AbortSignal) => Promise<T>): Promise<T> {
     const controller = new AbortController();
     const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
     return fn(controller.signal).finally(() => clearTimeout(timer));
   }

   async function readErrorBody(err: unknown): Promise<string> {
     if (err instanceof ResponseError) {
       const status = err.response.status;
       try {
         const text = await err.response.text();
         return `${status} ${text}`;
       } catch {
         return `${status} <body unreadable>`;
       }
     }
     return String(err);
   }

   /**
    * Create / upsert a contact and log a communication row in one shot.
    * Use for first-time events (web_form, booking.created).
    */
   export async function logConversion(input: LogConversionInput): Promise<void> {
     if (!process.env.CLIENTHUB_API_KEY) {
       console.warn("[client-hub] CLIENTHUB_API_KEY not set; skipping");
       return;
     }

     await withTimeout(async (signal) => {
       try {
         const contact = await contacts.createContactEndpointApiV1ContactsPost(
           {
             contactCreate: {
               contactType: "lead",
               firstName: input.firstName ?? "",
               lastName: input.lastName ?? "",
               emails: input.email
                 ? [{ address: input.email, isPrimary: true }]
                 : [],
               phones: input.phone
                 ? [{ number: input.phone, isPrimary: true }]
                 : [],
               externalRefsJson: {
                 source_page: input.sourcePage,
                 site_source_code:
                   input.siteSourceCode ?? process.env.CLIENTHUB_SOURCE_CODE,
                 referrer: input.referrer,
                 user_agent: input.userAgent,
                 ip_address: input.ipAddress,
                 gtm_client_id: input.gtmClientId,
                 utm: input.utm,
                 extra: input.extra,
               },
             },
           },
           { signal }, // SDK runtime spreads initOverrides into RequestInit
         );

         await communications.createCommunicationApiV1CommunicationsPost(
           {
             commCreate: {
               contactUuid: contact.uuid,
               channel: input.event,
               direction: "inbound",
               occurredAt: new Date().toISOString(),
               subject: input.subject,
               body: input.body,
             },
           },
           { signal },
         );
       } catch (err) {
         console.warn(
           `[client-hub] logConversion failed: ${await readErrorBody(err)}`,
         );
       }
     });
   }

   /**
    * Append a communication row to an EXISTING contact (looked up by
    * email). Use for follow-up events (booking.cancelled) so the rich
    * create-time external_refs_json on the contact row is not clobbered.
    * See "Don't shadow — merge" below for the full contract.
    */
   export async function appendCommunication(
     input: AppendCommunicationInput,
   ): Promise<void> {
     if (!process.env.CLIENTHUB_API_KEY) {
       console.warn("[client-hub] CLIENTHUB_API_KEY not set; skipping");
       return;
     }

     await withTimeout(async (signal) => {
       try {
         // LookupApi response is currently typed as `any` server-side
         // (no response_model on the FastAPI route); cast to the known
         // shape. Tracked as a v0.3.6+ TODO on the Client Hub project.
         const result = (await lookups.lookupEmailApiV1LookupEmailEmailGet(
           { email: input.email },
           { signal },
         )) as { matches?: Array<{ uuid: string }> };

         const matches = result.matches ?? [];
         if (!matches.length) {
           console.warn(
             `[client-hub] appendCommunication: no contact for ${input.email}`,
           );
           return;
         }

         await communications.createCommunicationApiV1CommunicationsPost(
           {
             commCreate: {
               contactUuid: matches[0].uuid,
               channel: input.event,
               direction: "inbound",
               occurredAt: new Date().toISOString(),
               subject: input.subject,
               body: input.body,
             },
           },
           { signal },
         );
       } catch (err) {
         console.warn(
           `[client-hub] appendCommunication failed: ${await readErrorBody(err)}`,
         );
       }
     });
   }

   /** Fire-and-forget version — does not await. */
   export function logConversionBackground(input: LogConversionInput): void {
     logConversion(input).catch(() => {});
   }

   /** Fire-and-forget version — does not await. */
   export function appendCommunicationBackground(
     input: AppendCommunicationInput,
   ): void {
     appendCommunication(input).catch(() => {});
   }

.. _client-hub-cp-usage:

**********************************************************************
Usage Example (Next.js API Route)
**********************************************************************

Call sites are unchanged from the legacy module — that's the whole
point of preserving the public surface above.

.. code-block:: typescript

   // app/api/contact/route.ts
   import { logConversionBackground } from "@/lib/client-hub";
   import { headers } from "next/headers";

   export async function POST(request: Request) {
     const body = await request.json();
     const hdrs = await headers();

     // Your existing form handling...
     // sendEmail(body);

     // Push to Client Hub (fire-and-forget — never blocks the response)
     logConversionBackground({
       event: "web_form",
       email: body.email,
       phone: body.phone,
       firstName: body.firstName,
       lastName: body.lastName,
       subject: `Contact form: ${body.subject}`,
       body: body.message,
       sourcePage: hdrs.get("referer") ?? undefined,
       userAgent: hdrs.get("user-agent") ?? undefined,
       ipAddress: hdrs.get("x-forwarded-for") ?? undefined,
     });

     return Response.json({ success: true });
   }

For booking-cancellation hooks, use ``appendCommunicationBackground``
instead so you log the cancellation without overwriting the rich
``external_refs_json`` from the original ``booking.created``:

.. code-block:: typescript

   // lib/scheduler-init.ts (booking.cancelled hook)
   import { appendCommunicationBackground } from "@/lib/client-hub";

   onBookingCancelled((booking) => {
     appendCommunicationBackground({
       event: "booking_cancelled",
       email: booking.customerEmail,
       subject: `Cancelled: ${booking.serviceName}`,
       body: `Appointment ${booking.appointmentId} cancelled`,
     });
   });

.. _client-hub-cp-payload-contract:

**********************************************************************
external_refs_json Payload Contract
**********************************************************************

Every integration MUST populate ``external_refs_json`` with as much
of the following shape as is available on the caller side. The
fields below are what the reference ``lib/client-hub.ts`` module
collects; consumers of Client Hub (reports, dashboards, Eaglesoft
sync, etc.) assume these paths.

.. code-block:: text

   {
     "source_page": "/book",                  # REQUIRED — URL path that fired the event
     "site_source_code": "my_website",        # REQUIRED — matches CLIENTHUB_SOURCE_CODE
     "referrer": "https://google.com/...",    # request referer header
     "ip_address": "203.0.113.42",            # from x-forwarded-for / x-real-ip
     "user_agent": "Mozilla/5.0 ...",         # from user-agent header
     "gtm_client_id": "GA1.1.1234.5678",      # GA4/GTM client ID if available
     "utm": {                                 # UTM parameters from the landing URL
       "source": "google",
       "medium": "cpc",
       "campaign": "summer-2026",
       "term": "...",
       "content": "..."
     },
     "extra": {                               # event-specific metadata
       "scheduler_event": "booking.created",  # which hook fired
       "appointment_id": 6,
       "service_name": "Filling",
       "staff_name": "Dr. Smith",
       "start_date": "2026-04-20T10:00:00Z",
       "total_price": "150.00"
     }
   }

.. rubric:: Mandatory fields

- ``source_page`` — the path/URL the event originated from
- ``site_source_code`` — used for cross-site reporting and source
  attribution filters
- Request headers (``user_agent``, ``ip_address``, ``referrer``)
  MUST be populated on **every** server-side POST. These are the
  minimum evidence needed to later investigate fraud, deduplicate
  leads across sites, and correlate with upstream analytics.

.. rubric:: Don't shadow — merge

Scheduler cancellation / update hooks must NOT POST a thinner
payload that overwrites the richer one from ``booking.created``.
When ``booking.cancelled`` fires, either:

1. **Preferred (built into the reference module):** call
   ``appendCommunicationBackground`` — it looks up the contact
   by email via ``LookupApi``, then POSTs only a new communication
   row, leaving the contact's ``external_refs_json`` untouched.
2. **If the hook legitimately needs to update the contact:** GET
   the current ``external_refs_json``, deep-merge the new fields
   in (do NOT replace), then ``PUT /api/v1/contacts/{uuid}``.

The dental care site hit this bug on 2026-04-11 — the
``booking.cancelled`` hook overwrote a rich ``booking.created``
payload with a 3-field stub. The reference module's
``appendCommunication`` shape is the regression-proof fix and is
the approach both production consumer sites use today.

.. _client-hub-cp-production-consumers:

**********************************************************************
Production Consumers
**********************************************************************

The list below tracks every site running against a Client Hub
production instance, the SDK version it pinned, and the cutover
commit. Add a row when a new site goes live; bump the version when
a site upgrades.

.. list-table::
   :header-rows: 1
   :widths: 22 22 18 22 16

   * - Site
     - Source code
     - SDK pin
     - Client Hub VPS
     - Cutover commit
   * - Complete Dental Care
       (``completedentalcarecolumbia.com``)
     - ``complete_dental_care_website``
     - ``^0.3.5``
     - ``client-hub-complete-dental-care.onlinesalessystems.com``
     - ``0b46c9e`` (2026-05-05)
   * - Clever Orchid
       (``cleverorchid.com``)
     - ``clever_orchid_website``
     - ``^0.3.5``
     - ``client-hub-clever-orchid.onlinesalessystems.com``
     - ``6524034`` (2026-05-05)

Both consumer sites use only ``ContactsApi``,
``CommunicationsApi``, and ``LookupApi`` from the SDK today —
the rest of the surface (``OrdersApi``, ``InvoicesApi``,
``AffiliationsApi``, ``MarketingSourcesApi``, ``AdminApi``,
``SpamPatternsApi``, etc.) is installed-but-unused. Plan accordingly
when shipping changes that affect those classes — see the
"Changes that need consumer-side coordination" rubric below.

.. rubric:: Changes that need consumer-side coordination

When changing the SDK, the matrix to think about:

1. **Changes to** ``ContactsApi`` / ``CommunicationsApi`` /
   ``LookupApi`` — these affect both production consumer sites.
   Breaking changes here need a coordinated bump and a fresh
   handoff prompt under ``docs/handoffs/``.
2. **Changes to any other API class** — safe to make freely; no
   active consumer reads them today.
3. **OpenAPI spec → SDK regeneration cadence** — every Client Hub
   release auto-publishes the matching SDK version via
   ``.github/workflows/publish-sdk.yml``. Consumer sites pinned at
   ``^0.3.x`` pick up patch versions on their next ``npm install``;
   ``0.4.x`` is opt-in.

.. _client-hub-cp-checklist:

**********************************************************************
Checklist for new integrations
**********************************************************************

Before wiring a new Web Factory site to Client Hub, verify the
following in the site's ``lib/client-hub.ts`` and every caller:

- [ ] ``.npmrc`` configured for ``@bradstancel:registry=...``;
  ``NPM_TOKEN`` set as the install-time consumer token
- [ ] ``@bradstancel/clienthub-sdk@^0.3.5`` (or current published
  version) added to ``package.json`` and resolved in
  ``package-lock.json``
- [ ] ``CLIENTHUB_URL`` / ``CLIENTHUB_API_KEY`` /
  ``CLIENTHUB_SOURCE_CODE`` set in ``.env.local`` and on the
  production VPS
- [ ] ``site_source_code`` included in every ``external_refs_json``
- [ ] Every ``logConversion`` / ``logConversionBackground``
  caller passes ``sourcePage``, ``userAgent``, ``ipAddress``,
  ``referrer`` (read from ``next/headers`` or equivalent on the
  server)
- [ ] UTM parameters parsed from the landing URL and passed
  through on the first server-side call of the session
- [ ] Scheduler / booking hooks populate the ``extra`` object with
  ``scheduler_event``, ``appointment_id``, ``service_name``,
  ``staff_name``, ``start_date``, ``total_price``
- [ ] ``booking.cancelled`` / update hooks call
  ``appendCommunicationBackground`` (NOT ``logConversionBackground``)
  so the rich create-time ``external_refs_json`` is not clobbered
- [ ] Add a row to the *Production Consumers* table above with the
  cutover commit
- [ ] End-to-end smoke test: submit a booking, cancel it, query
  ``SELECT external_refs_json FROM contacts ORDER BY created_at
  DESC LIMIT 1`` — every field above should be populated
