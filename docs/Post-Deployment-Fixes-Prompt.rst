.. _post-deployment-fixes-prompt:

######################################################################
Client Hub — Post-Deployment Fixes & Enhancements Prompt
######################################################################

:Target audience: Claude Code session opened in ``~/docker/client-hub/``
:Created: 2026-04-11 (post first real VPS deployment)
:Companion: ``docs/Installation-Implementation-Prompt.rst``
:Context: This prompt captures everything found during the first
          real production deployment on
          ``client-hub-complete-dental-care.onlinesalessystems.com``
          that followed the original Installation-Implementation-Prompt.
          Two bugs were fixed live. Several improvements and a
          production cleanup task remain.


.. contents:: Table of Contents
   :local:
   :depth: 2


**********************************************************************
How to use this document
**********************************************************************

Read this in full before starting. Use ``TaskCreate`` to break it
into tracked tasks. Execute the sections in order (Section 3 has a
cleanup item that needs to run FIRST against the live VPS). Commit
in logical chunks with clear messages and push to master.

When everything is green, tell the parent session (in
``~/Sites/complete-dental-care-nextjs``) that client-hub is fully
hardened so the dental care site's operator can stop worrying
about test pollution.


**********************************************************************
Section 1 — Already fixed during the first deployment
**********************************************************************

These two bugs were caught live and fixed in commits on master.
**Do not re-implement them.** They're listed here so you have the
full history and don't get confused by the install.sh /
docker-compose.bundled.yml diffs.

Bug 1 — install.sh pre-created the backups dir before git clone
======================================================================

**Commit:** ``93dc449 fix(install): don't pre-create INSTALL_DIR/backups before git clone``

``scripts/install.sh`` previously did:

.. code-block:: bash

   mkdir -p "$INSTALL_DIR" "$INSTALL_DIR/backups" /var/log/client-hub
   ... later ...
   git clone "$REPO_URL" "$INSTALL_DIR"

``git clone`` refuses to clone into a non-empty directory, so every
fresh install failed with::

    fatal: destination path '/opt/client-hub' already exists
    and is not an empty directory.

**Fix:** moved the ``mkdir -p "$INSTALL_DIR/backups"`` and its
``chown/chmod`` to AFTER the clone. Only ``/var/log/client-hub`` is
created before the clone. Also added a check that fails loudly if
``$INSTALL_DIR`` exists but is not a git repo, so a stale directory
won't be silently clobbered.

Bug 2 — bundled+TLS compose didn't bind API port to host
======================================================================

**Commit:** ``5dbf511 fix(compose): bind API to 127.0.0.1:8800 in bundled+TLS mode``

In the original ``docker-compose.bundled.yml``, the
``client-hub-api`` service had no ``ports:`` mapping in bundled+TLS
mode. The API was reachable only via the internal Docker network,
so ``install.sh``'s post-migration steps that used
``curl http://127.0.0.1:8800/api/v1/...`` all timed out::

    [client-hub] FATAL: API did not become healthy within 60 seconds

**Fix:** added ``ports: - "127.0.0.1:8800:8800"`` to the API
service in ``docker-compose.bundled.yml``. Loopback-only binding so
UFW still blocks the port externally and Caddy remains the only
public path, but local processes on the VPS (install.sh,
smoke-test.sh, operator scripts, future OpsInsights tunnel) can
reach the API directly without going through TLS termination.


**********************************************************************
Section 2 — Smoke test bug (needs investigation + fix)
**********************************************************************

The installer's smoke test at the end of the successful install
reported 1 failure out of 7:

.. code-block:: text

    Testing health endpoint...
      [PASS] GET /api/v1/health returns 200
      [PASS] Database is connected
      [PASS] GET /openapi.json returns 200
      [FAIL] GET /contacts without key returns 401
      [PASS] GET /contacts with key returns 200
      [PASS] GET /settings with key returns 200
      [PASS] GET /admin/sources with root key returns 200

    Results: 6 passed, 1 failed

The smoke test expects an unauthenticated ``GET /api/v1/contacts``
to return 401. The actual response is something else (almost
certainly 403 — FastAPI's default when an ``X-API-Key`` dependency
is missing is ``403 Forbidden``, not 401).

.. rubric:: What to do

1. Run the same request yourself and see the real code::

     curl -i http://127.0.0.1:8800/api/v1/contacts 2>&1 | head -5

2. Decide whether the **test** is wrong (assertion should match
   reality: 403) or the **API** is wrong (FastAPI middleware should
   explicitly return 401 with ``WWW-Authenticate`` header for
   semantic correctness).

3. I recommend **both**: make the API explicitly return 401 for
   missing auth (more semantically correct — 401 means "no/bad
   credentials", 403 means "valid credentials, access denied"),
   AND also accept 403 in the smoke test assertion for
   backwards compatibility.

4. Update the assertion in ``scripts/smoke-test.sh`` to be one of
   ``401|403`` or rewrite the middleware to return 401. Your call.

5. Re-run the smoke test and confirm 7/7 pass.


**********************************************************************
Section 3 — Clean up test data on the live VPS (do this FIRST)
**********************************************************************

The first production install at
``client-hub-complete-dental-care.onlinesalessystems.com`` picked
up the seed data from ``migrations/012_seed_test_data.sql`` because
``scripts/bootstrap-migrations.sh`` runs every ``migrations/*.sql``
file with no mode filter. As a result, the production database has:

- 5 test contacts from ``012_seed_test_data.sql``:
  Sarah Johnson, Dr. Michael Chen, Emily Rodriguez, James Smith,
  and "Thread Supply Co" (an organization contact)
- 1 ``Smoke Test`` contact created during post-install verification
- 1 ``E2E TestRun...`` contact created during the end-to-end test
  from the dental care site

These all need to be removed from production **before** Section 4's
schema/migration restructuring work. Otherwise whatever mechanism
you add to skip seed data won't help the already-contaminated DB.

.. rubric:: Approach

Write a new ``scripts/cleanup-test-data.sh`` that:

1. **Runs against a live instance over SSH** with a ``--host``
   flag — not locally against Cybertron's dev instance
2. **Dry-run by default.** Use ``--apply`` to actually delete.
3. **Deletes contacts matching any of:**

   - ``last_name = 'Test'`` AND ``first_name = 'Smoke'``
   - ``last_name LIKE 'TestRun%'``
   - ``first_name IN ('Sarah', 'Emily', 'James', 'Thread') AND
     last_name IN ('Johnson', 'Rodriguez', 'Smith', 'Supply Co')``
     — or, more conservatively, match on the exact UUIDs from
     ``012_seed_test_data.sql`` if you can derive them
   - ``first_name = 'Dr. Michael' AND last_name = 'Chen'``

4. **Cascades** to:

   - ``contact_emails``, ``contact_phones``, ``contact_addresses``
   - ``contact_tag_map``, ``contact_marketing_sources``
   - ``contact_channel_prefs``, ``contact_preferences``
   - ``contact_notes``
   - ``communications`` (via ``contact_id``)
   - ``orders`` → ``order_items`` → ``order_status_history``
   - ``invoices`` → ``payments``

   You may be able to use existing ON DELETE CASCADE FKs where
   they exist; otherwise delete children-first.

5. **Prints a summary** of what was deleted (count per table)
6. **Logs the SQL it ran** to ``/var/log/client-hub/cleanup.log``
   on the target host for audit

.. rubric:: Alternative — one-shot SQL dump for Brad to run manually

If writing a full script is overkill for a one-time cleanup, also
provide a simple ``docs/Cleanup-Test-Data.rst`` with an SQL snippet
Brad can run via ``mariadb`` over the SSH tunnel. Either approach
is fine — pick the one that fits the project style.

.. rubric:: Run it

After writing the cleanup:

1. Dry-run against production::

     ssh root@client-hub-complete-dental-care.onlinesalessystems.com \
       "cd /opt/client-hub && docker compose -f docker-compose.bundled.yml \
        exec -T mariadb mariadb -uroot -p\$(grep MARIADB_ROOT_PASSWORD .env | cut -d= -f2) clienthub" \
       < /opt/client-hub/scripts/cleanup-test-data.sql  # or similar

2. Review the dry-run output
3. Apply for real
4. Verify ``SELECT COUNT(*) FROM contacts`` shows only what Brad expects


**********************************************************************
Section 4 — Production-safe seed data handling (the real fix)
**********************************************************************

The root cause of Section 3's problem is that every migration in
``migrations/*.sql`` runs on every install. Test data migration
``012_seed_test_data.sql`` has no business running in production.

.. rubric:: Recommended approach

Pick ONE of these; my preference is A.

.. rubric:: Option A — separate directory (my recommendation)

1. Create ``migrations/dev/`` directory
2. Move ``012_seed_test_data.sql`` → ``migrations/dev/012_seed_test_data.sql``
3. Update ``scripts/bootstrap-migrations.sh`` to:

   - Always run every ``migrations/*.sql`` file (schema migrations)
   - Only run ``migrations/dev/*.sql`` when ``--with-seed-data`` is passed
   - Track dev migrations in the same ``_schema_migrations`` table
     with a ``dev/`` prefix so they're visibly separated
4. Update CI workflow (``.github/workflows/ci.yml``) to run both
   — CI needs the test data for the test suite
5. Update ``scripts/install.sh`` to NOT pass ``--with-seed-data``
   by default. Add an ``--include-seed-data`` installer flag for
   anyone who wants test data on a dev install.
6. Document in ``docs/Deployment.rst``:

   - How seed data works
   - When to use ``--include-seed-data``
   - How to clean up if you accidentally installed with seed data

.. rubric:: Option B — filename convention (simpler, more fragile)

Rename ``012_seed_test_data.sql`` → ``012_seed_test_data.dev.sql``
and update ``bootstrap-migrations.sh`` to skip any ``*.dev.sql``
file unless ``--with-dev-migrations`` is set. Simpler diff, but
harder to extend if you later add more dev-only migrations.

.. rubric:: Option C — env var check inside the migration

Wrap the INSERT statements inside ``012_seed_test_data.sql`` in an
``IF`` check against a session variable that the runner sets only
in dev mode. Works but couples the migration file tightly to the
runner's behavior and is harder to read.

**Don't pick Option C.**

.. rubric:: Backport the fix to the already-installed VPS

After the option is implemented and tests pass, Brad will
``git pull`` on the VPS to get the new bootstrap-migrations.sh and
install.sh. The test data cleanup from Section 3 already handles
the existing pollution. New installs get clean DBs from the start.


**********************************************************************
Section 5 — Installer hardening
**********************************************************************

Several smaller installer improvements caught during the real
deployment:

5a. Add ``--include-seed-data`` flag
======================================================================

Per Section 4 above. Opt-in, default off.

5b. Installer should pre-flight DNS
======================================================================

When ``--domain`` is provided, the installer should verify the
domain resolves to the local public IP **before** docker compose up
— Caddy's Let's Encrypt challenge will fail silently otherwise and
the user gets confused. Add::

    verify_dns() {
        local domain="$1"
        local my_ip
        my_ip=$(curl -sf https://api.ipify.org || echo "")
        local resolved
        resolved=$(dig +short A "$domain" | head -1)
        if [[ -z "$my_ip" || -z "$resolved" ]]; then
            warn "Could not verify DNS for $domain — proceeding, but Caddy may fail to get a cert"
            return
        fi
        if [[ "$my_ip" != "$resolved" ]]; then
            warn "Domain $domain resolves to $resolved but this host is $my_ip. Caddy TLS will fail."
        fi
    }

Non-fatal warning, not a hard abort.

5c. Installer should detect an existing install and offer upgrade path
======================================================================

Right now if you run ``install.sh`` a second time on a box that
already has client-hub, you get the
"``$INSTALL_DIR exists but is not a git repo``" failure I just
added. That's correct for a stale directory but wrong for an
intentional upgrade. Make it smarter:

- If ``$INSTALL_DIR/.git`` exists → offer to ``git pull`` + rerun
  migrations + rebuild compose (upgrade path)
- If ``$INSTALL_DIR`` exists without ``.git`` → fail loudly
  (protect against accidental clobber)
- Optionally add ``--upgrade`` flag that makes this explicit

5d. Installer should write a docker-compose override stub for OpsInsights
==========================================================================

``docs/Deployment.rst`` currently explains how to expose MariaDB to
``127.0.0.1:3306`` via a manual override file. Brad is the only user
right now, and he'll forget the recipe. Have the installer drop a
commented-out ``docker-compose.override.yml.example`` next to the
bundled compose, with the MariaDB host-port binding snippet ready to
uncomment::

    # docker-compose.override.yml.example
    #
    # Copy to docker-compose.override.yml (no .example suffix) to
    # enable OpsInsights / local mariadb client access over an SSH
    # tunnel:
    #   ssh -N -L 13306:127.0.0.1:3306 root@client-hub.example.com
    #
    # services:
    #   mariadb:
    #     ports:
    #       - "127.0.0.1:3306:3306"

5e. Uninstall should preserve the install summary
======================================================================

Right now ``scripts/uninstall.sh`` (per the prompt) preserves
backups. It should also preserve
``/opt/client-hub/.install-summary`` and the ``.env`` file in a
``/root/client-hub-saved/`` directory so credentials aren't lost if
someone runs uninstall to rebuild. Or at minimum, print a big
warning before deletion asking to confirm.


**********************************************************************
Section 6 — API / SDK improvements (smaller items)
**********************************************************************

6a. ``GET /api/v1/lookup/email/{email}`` — include all contact methods
======================================================================

During end-to-end testing I noticed this endpoint returned
``"phone": null`` for a contact that definitely had a phone number
set (the dental care form submitted both an email and a phone).
The lookup response should include ALL of the contact's phones and
emails, not just the email that was looked up. It's a lookup for
intelligence, so return the full context.

Check ``api/app/routers/lookup.py`` or equivalent and update the
Pydantic response schema to include a list of phones alongside the
email.

6b. Contact dedup via email / phone
======================================================================

Right now, every form submission creates a new contact row even
if that email already exists in the DB. This is by design for v1
but creates dupes over time. Consider adding:

- A new endpoint ``POST /api/v1/contacts/upsert`` that:

  1. Looks up existing contact by primary email (if provided)
  2. If found, updates the contact and adds a new communication
  3. If not found, creates a new contact + communication

- Or: update the existing ``POST /api/v1/contacts`` to do the
  upsert semantically (risk: behavior change for existing callers)

- Or: leave the API alone, and update the reference
  ``lib/client-hub.ts`` in ``docs/Cross-Project-Integration.rst``
  to call ``/lookup/email`` first and then either POST a new
  contact or POST only a communication to an existing one

Brad's preference will drive this. Ask before implementing — this
is a semantic change that affects every integration.

6c. ``GET /api/v1/admin/events`` — cross-source event reporting
======================================================================

Right now the only way to see events filtered by source is to
raw-SQL the ``v_events_by_source`` view. Add a root-key-only admin
endpoint that exposes the view over HTTP with filter params:

- ``?source_code=...``
- ``?channel_code=...``
- ``?from=YYYY-MM-DD``
- ``?to=YYYY-MM-DD``
- ``?limit=...``

This unblocks future admin UIs and makes it easy for Brad to pull
monthly reports via curl.


**********************************************************************
Section 7 — Docs
**********************************************************************

- Update ``CHANGELOG.rst`` with everything in this prompt
- Update ``docs/Deployment.rst`` to document:

  - The ``--include-seed-data`` flag
  - The DNS pre-flight check behavior
  - The upgrade path for ``install.sh`` on existing instances
  - The ``docker-compose.override.yml.example`` file
- Update ``TODO.rst``: mark the items here as done; add any new
  items discovered during implementation
- Update ``docs/Installation-Implementation-Prompt.rst`` (the
  original prompt) with a footer that says "see
  docs/Post-Deployment-Fixes-Prompt.rst for the second pass"


**********************************************************************
Section 8 — Non-goals
**********************************************************************

Explicitly out of scope for this pass:

- Refactoring the auth middleware beyond Section 2's 401-vs-403 fix
- Adding new entity types to the schema
- Building an admin UI beyond the single new
  ``/admin/events`` endpoint in Section 6c
- Live InvoiceNinja / Chatwoot / Zammad integrations
- Kubernetes / non-docker-compose deployment targets
- Multi-company multi-tenancy (still one DB per company)
- Changing the data-first philosophy or the ``external_refs_json``
  convention


**********************************************************************
Section 9 — Success criteria
**********************************************************************

Done when:

- [ ] Section 3 cleanup has run against the live VPS and
  ``SELECT COUNT(*) FROM contacts WHERE last_name IN ('Test', 'Rodriguez',
  'Smith', 'Johnson', 'Chen') OR last_name LIKE 'TestRun%'`` returns 0
- [ ] Section 4's seed-data separation is implemented in one of the
  three options (A recommended); fresh installs no longer pick up
  ``012_seed_test_data.sql``
- [ ] Section 2's smoke test bug is resolved — ``smoke-test.sh``
  reports 7/7 passing
- [ ] Section 5 installer hardening items are implemented (DNS
  pre-flight, upgrade path, override example file)
- [ ] Section 6a (lookup include phones) is fixed
- [ ] Section 6b is **discussed** with Brad before any code change
- [ ] Section 6c admin events endpoint is implemented and has tests
- [ ] All new code passes ``ruff``, ``shellcheck``, and ``rstcheck``
- [ ] ``pytest api/tests/ -v`` still passes (CI green)
- [ ] ``CHANGELOG.rst``, ``TODO.rst``, ``docs/Deployment.rst``
  updated


**********************************************************************
Section 10 — Verification after all fixes ship
**********************************************************************

Brad will (or ask the parent session to):

1. ``git pull`` on
   ``client-hub-complete-dental-care.onlinesalessystems.com``
2. Run ``./scripts/bootstrap-migrations.sh`` (should be a no-op now
   that seed data is gone)
3. Re-run ``./scripts/smoke-test.sh`` — expect 7/7
4. Submit a test form on ``completedentalcarecolumbia.com`` and
   verify the new contact appears in client-hub exactly as before
5. Tear down and reinstall from scratch on a throwaway DO droplet
   to verify the install flow still works end-to-end with
   ``--include-seed-data`` both set and unset
6. Close out the TODO items in the dental care repo


**********************************************************************
References
**********************************************************************

- Original prompt:
  ``~/docker/client-hub/docs/Installation-Implementation-Prompt.rst``
- Dental care repo (first consumer):
  ``~/Sites/complete-dental-care-nextjs/``
- Dental care ``lib/client-hub.ts`` reference integration:
  ``~/Sites/complete-dental-care-nextjs/lib/client-hub.ts``
- Dental care scheduler hook wiring:
  ``~/Sites/complete-dental-care-nextjs/lib/scheduler-init.ts``
- Live production instance:
  ``https://client-hub-complete-dental-care.onlinesalessystems.com``
- Production VPS SSH:
  ``ssh -p22 root@client-hub-complete-dental-care.onlinesalessystems.com``
- First deployment commits that shipped:
  ``93dc449 fix(install): don't pre-create INSTALL_DIR/backups before git clone``
  ``5dbf511 fix(compose): bind API to 127.0.0.1:8800 in bundled+TLS mode``
