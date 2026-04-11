.. _client-hub-data-privacy:

######################################################################
Client Hub — Data Privacy & PII Handling
######################################################################

.. _client-hub-privacy-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub stores **real PII** (personally identifiable information)
by deliberate design decision. This document describes what is
stored, why, and how to handle privacy obligations.

.. _client-hub-privacy-what:

**********************************************************************
PII Fields Stored
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Field
     - Location
     - Notes
   * - Full name
     - ``contacts.first_name``, ``contacts.last_name``
     - When provided by the user
   * - Email addresses
     - ``contact_emails.email_address``
     - Multiple per contact, with type labels
   * - Phone numbers
     - ``contact_phones.phone_number``
     - E.164 format preferred
   * - Physical addresses
     - ``contact_addresses.*``
     - Street, city, state, postal, country
   * - IP addresses
     - ``external_refs_json.ip_address``
     - From web form submissions
   * - User agent strings
     - ``external_refs_json.user_agent``
     - From web form submissions
   * - UTM parameters
     - ``external_refs_json.utm.*``
     - Campaign attribution data

.. _client-hub-privacy-why:

**********************************************************************
Why Real Data (Not Hashed)
**********************************************************************

Brad made the explicit decision to store real PII because:

1. **Richer enrichment** — Real data can be cross-referenced with
   enrichment APIs to fill in missing details
2. **Better ad attribution** — Real IPs and UTM data enable accurate
   campaign ROI analysis
3. **Better customer follow-up** — Staff can see and use contact
   details without an extra decryption step
4. **CTI integration** — Phone lookup must return readable names and
   numbers for caller ID display

.. _client-hub-privacy-retention:

**********************************************************************
Data Retention
**********************************************************************

Default retention: **2 years** from last activity. No automatic
purge is currently implemented — this is a future TODO.

To change retention policy, implement a scheduled job that:

1. Identifies contacts with no activity in the retention period
2. Anonymizes or deletes their PII
3. Preserves aggregated analytics data

.. _client-hub-privacy-deletion:

**********************************************************************
Handling Deletion Requests
**********************************************************************

To delete a contact's PII (e.g., GDPR right to erasure):

.. code-block:: sql

   -- Replace CONTACT_UUID with the actual UUID
   SET @cid = (SELECT id FROM contacts WHERE uuid = 'CONTACT_UUID');

   -- Delete detail records (CASCADE handles most)
   DELETE FROM contact_phones WHERE contact_id = @cid;
   DELETE FROM contact_emails WHERE contact_id = @cid;
   DELETE FROM contact_addresses WHERE contact_id = @cid;
   DELETE FROM contact_notes WHERE contact_id = @cid;
   DELETE FROM contact_preferences WHERE contact_id = @cid;
   DELETE FROM contact_channel_prefs WHERE contact_id = @cid;
   DELETE FROM contact_marketing_sources WHERE contact_id = @cid;
   DELETE FROM contact_tag_map WHERE contact_id = @cid;

   -- Anonymize the contact record (preserve for FK integrity)
   UPDATE contacts SET
     first_name = 'DELETED',
     last_name = 'DELETED',
     display_name = NULL,
     date_of_birth = NULL,
     notes_text = NULL,
     external_refs_json = NULL,
     is_active = FALSE,
     deleted_at = NOW()
   WHERE id = @cid;

.. _client-hub-privacy-logging:

**********************************************************************
Logging Policy
**********************************************************************

The API **never logs** full IPs, user agents, emails, or phone
numbers at INFO level. These appear only at DEBUG level, which
should not be enabled in production.

TLS is enforced for all public-facing deployments via Caddy with
automatic Let's Encrypt certificates.
