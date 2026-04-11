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
portable — drop in the reference module, set three env vars, and
start pushing events.

.. _client-hub-cp-env-vars:

**********************************************************************
Environment Variables
**********************************************************************

Add to your Next.js site's ``.env.local``:

.. code-block:: text

   CLIENTHUB_URL=https://client-hub.example.com
   CLIENTHUB_API_KEY=your_source_scoped_api_key_here
   CLIENTHUB_SOURCE_CODE=my_website

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
Reference Module: lib/client-hub.ts
**********************************************************************

Drop this file into your Next.js project at ``lib/client-hub.ts``:

.. code-block:: typescript

   // lib/client-hub.ts
   // Send conversion events to Client Hub. Error-swallowing — never crashes caller.

   const CLIENTHUB_URL = process.env.CLIENTHUB_URL || "https://client-hub.example.com";
   const CLIENTHUB_API_KEY = process.env.CLIENTHUB_API_KEY || "";
   const TIMEOUT_MS = 3000;

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

   export async function logConversion(input: LogConversionInput): Promise<void> {
     if (!CLIENTHUB_API_KEY) {
       console.warn("[client-hub] CLIENTHUB_API_KEY not set; skipping");
       return;
     }

     const occurredAt = new Date().toISOString();
     const externalRefs = {
       source_page: input.sourcePage,
       referrer: input.referrer,
       user_agent: input.userAgent,
       ip_address: input.ipAddress,
       gtm_client_id: input.gtmClientId,
       utm: input.utm,
       extra: input.extra,
     };

     const controller = new AbortController();
     const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

     try {
       // 1. Create / upsert contact
       const contactRes = await fetch(`${CLIENTHUB_URL}/api/v1/contacts`, {
         method: "POST",
         headers: {
           "Content-Type": "application/json",
           "X-API-Key": CLIENTHUB_API_KEY,
         },
         body: JSON.stringify({
           contact_type: "lead",
           first_name: input.firstName ?? "",
           last_name: input.lastName ?? "",
           emails: input.email ? [{ address: input.email, is_primary: true }] : [],
           phones: input.phone ? [{ number: input.phone, is_primary: true }] : [],
           external_refs_json: externalRefs,
         }),
         signal: controller.signal,
       });

       if (!contactRes.ok) {
         console.warn(`[client-hub] contact create failed: ${contactRes.status}`);
         return;
       }

       const contact = (await contactRes.json()) as { uuid: string };

       // 2. Log the event
       await fetch(`${CLIENTHUB_URL}/api/v1/communications`, {
         method: "POST",
         headers: {
           "Content-Type": "application/json",
           "X-API-Key": CLIENTHUB_API_KEY,
         },
         body: JSON.stringify({
           contact_uuid: contact.uuid,
           channel: input.event,
           direction: "inbound",
           occurred_at: occurredAt,
           subject: input.subject,
           body: input.body,
         }),
         signal: controller.signal,
       });
     } catch (err) {
       console.warn("[client-hub] event failed:", err);
     } finally {
       clearTimeout(timeoutId);
     }
   }

   /** Fire-and-forget version — does not await. */
   export function logConversionBackground(input: LogConversionInput): void {
     logConversion(input).catch(() => {});
   }

.. _client-hub-cp-usage:

**********************************************************************
Usage Example (Next.js API Route)
**********************************************************************

.. code-block:: typescript

   // app/api/contact/route.ts
   import { logConversion } from "@/lib/client-hub";
   import { headers } from "next/headers";

   export async function POST(request: Request) {
     const body = await request.json();
     const hdrs = await headers();

     // Your existing form handling...
     // sendEmail(body);

     // Push to Client Hub (fire-and-forget)
     logConversion({
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
     }).catch(() => {}); // Never block the response

     return Response.json({ success: true });
   }
