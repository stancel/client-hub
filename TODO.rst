.. _client-hub-todo:

######################################################################
Client Hub — TODO
######################################################################

.. _client-hub-todo-phase1:

Phase 1 — Data Model Design [COMPLETE]
======================================================================

- [x] Design 3NF data model (initial: 31 tables + 2 views;
  after Phases 8–9: 34 tables + 3 views; latest after Phase 16:
  39 tables + 3 views)
- [x] Document all tables, columns, types, constraints, indexes, FKs
- [x] Document normalization rationale (1NF, 2NF, 3NF analysis)
- [x] Document junction tables and why they exist
- [x] Include entity-relationship summary
- [x] Write comprehensive ``docs/data-model.rst``
- [x] Add marketing opt-out boolean flags (sms, email, phone)
- [x] Add contact_preferences table (flexible key-value)
- [x] Create v_contact_summary and v_contact_last_order views

.. _client-hub-todo-phase2:

Phase 2 — Schema Implementation [COMPLETE]
======================================================================

- [x] Create ``migrations/`` directory with numbered SQL files
- [x] Write DDL for all tables and views (migrations 001-018;
  012 is dev/CI-only seed data relocated to ``migrations/dev/``)
- [x] Execute all migrations against ``clienthub`` via MCP tools
- [x] Verify schema with ``search_objects`` MCP tool
- [x] Seed lookup tables with initial reference data (58 rows)

.. _client-hub-todo-phase3:

Phase 3 — Test Data and Validation [COMPLETE]
======================================================================

- [x] Insert realistic test data exercising all relationships
- [x] Ran 11 validation queries — all passed with zero issues
- [x] Validated: FK integrity, orphan checks, CTI/Chatwoot lookups,
  conversion flow, order chain, junction tables, opt-outs, provenance

.. _client-hub-todo-phase4:

Phase 4 — REST API Design [COMPLETE]
======================================================================

- [x] Create ``docs/api-design.rst``
- [x] Design CTI lookup endpoints (phone, email)
- [x] Design CRUD endpoints for all core entities
- [x] Design webhook endpoints (InvoiceNinja, Chatwoot)
- [x] Design preference and marketing opt-out endpoints
- [x] Design customer intelligence endpoints
- [x] Define authentication approach (API key)
- [x] Choose API framework (Python FastAPI + SQLAlchemy)
- [x] Document TDD testing strategy
- [x] Document SDK generation workflow (Python, PHP, TypeScript)
- [x] **GATE: Brad approved the design**

.. _client-hub-todo-phase5:

Phase 5 — API Implementation (TDD) [COMPLETE]
======================================================================

Initial API: 63 tests / 13 files / 23 endpoint paths.
Current after Phases 8–10: **89 tests / 17 files / 28 paths**.

- [x] Scaffold API project in ``api/`` directory
- [x] Set up pytest + httpx test infrastructure with real DB
- [x] Implement and test: health, lookup, contacts CRUD, conversion,
  preferences, marketing opt-outs, intelligence, organizations,
  orders, invoices, payments, communications, webhooks, settings
- [x] Add API container to ``docker-compose.yml`` on ``my-main-net``
- [x] Container running, all endpoints verified with curl
- [x] OpenAPI spec at ``/openapi.json`` (28 paths)

.. _client-hub-todo-phase6:

Phase 6 — SDK Generation [COMPLETE]
======================================================================

- [x] Created ``scripts/generate-sdks.sh`` (Docker-based)
- [x] Generated Python SDK in ``sdks/python/``
- [x] Generated PHP SDK in ``sdks/php/``
- [x] Generated TypeScript SDK in ``sdks/typescript/``
- [x] All SDKs have 10 API classes matching every router

.. _client-hub-todo-phase7:

Phase 7 — CI/CD Pipeline [COMPLETE]
======================================================================

- [x] GitHub Actions CI: ``.github/workflows/ci.yml``
- [x] Pipeline: lint (ruff + rstcheck) → test (MariaDB service) →
  build → SDK generation
- [x] ruff lint config, all Python code passing
- [x] All RST docs passing rstcheck
- [x] Documented in ``docs/ci-cd.rst``

.. _client-hub-todo-phase8:

Phase 8 — Multi-Source + Installer [COMPLETE]
======================================================================

- [x] Migrations 014-018 (sources, api_keys, source_id columns,
  channel types, views, tracking table)
- [x] Multi-source auth middleware (root key + per-source keys)
- [x] Admin router for sources and API key management
- [x] Auto-stamp source_id on contacts and communications
- [x] 78 tests passing (63 original + 15 new)
- [x] One-line installer (``scripts/install.sh``)
- [x] Bundled Docker compose files (with/without TLS)
- [x] Backup, uninstall, smoke-test, migration runner scripts
- [x] Full documentation: Multi-Source, Deployment, Cross-Project
  Integration, Data Privacy, Upgrade guide
- [x] Updated CI workflow with shellcheck + new migrations

.. _client-hub-todo-phase9:

Phase 9 — Post-Deployment Fixes [COMPLETE]
======================================================================

- [x] Smoke test fix (curl -sf → -s, accept 401/403)
- [x] Seed data separated (migrations/dev/, --with-seed-data flag)
- [x] Cleanup script for contaminated production instances
- [x] Installer hardening (DNS preflight, --include-seed-data)
- [x] Override example for OpsInsights access
- [x] Uninstall preserves credentials to /root/client-hub-saved/
- [x] Lookup returns all phones/emails (not just matched)
- [x] Admin events endpoint (GET /admin/events with filters)
- [x] 82 tests passing

.. _client-hub-todo-phase10:

Phase 10 — external_refs_json Data-Loss Fix [COMPLETE]
======================================================================

- [x] Pydantic schemas for Contact/Organization/Order now accept
  ``external_refs_json: dict[str, Any] | None`` (was silently
  stripped before reaching the service layer)
- [x] Serialize dict → JSON string on write, defensive
  ``json.loads`` on read
- [x] 7 new round-trip tests (89 total; was 82)
- [x] Round-trip verified on live dental care VPS
  (commit ``fa6bf2d``)
- [x] Payload contract documented in
  ``docs/Cross-Project-Integration.rst``
- [x] Handoff prompt
  ``docs/Dental-Care-Payload-Fix-Prompt.rst`` created for the
  thin-payload + booking.cancelled overwrite issues discovered
  during verification

.. _client-hub-todo-phase11:

Phase 11 — Multi-Org Affiliations + Schema Standardization [COMPLETE]
======================================================================

Data model went from "contact has at most one organization" to proper
many-to-many via ``contact_org_affiliations``. Schema name
standardized on ``clienthub`` across code, CI, docs, and live
Cybertron local MariaDB.

- [x] Design: ``docs/data-model.rst`` + ``docs/api-design.rst``
  sections for ``contact_org_affiliations``, ``seniority_levels``,
  affiliation_id on contact_phones/emails/addresses
- [x] ``docs/Migration-Strategy.rst`` playbook codifying the
  idempotent-numbered-migration + TDD-first pattern
- [x] Migration 019 — ``contact_org_affiliations`` junction +
  ``seniority_levels`` lookup + backfill from
  ``contacts.organization_id``
- [x] Migration 020 — nullable ``affiliation_id`` FK on
  contact_phones, contact_emails, contact_addresses
- [x] Migration 021 — drop ``contacts.organization_id`` +
  rewrite ``v_contact_summary`` to source org from primary
  affiliation
- [x] Migration 022 — generated-column partial-unique indexes
  enforcing "at most one primary per contact" on detail tables
- [x] New affiliation endpoints under
  ``/api/v1/contacts/{uuid}/affiliations`` (list/create/update/delete)
  with service-layer primary promotion/demotion
- [x] Clean break of ``/api/v1`` (no dual versioning) —
  ``organization_uuid`` on Contact removed; new
  ``primary_organization_uuid`` + ``affiliations`` list in responses
- [x] 101 tests passing (89 + 12 new affiliation tests)
- [x] Schema rename ``dev_schema`` → ``clienthub`` across all
  code, CI, docs; Cybertron local DB renamed end-to-end
- [x] Sister ``~/docker/mariadb/`` project standardized on
  ``clienthub`` default (``.env``, ``.env.example``,
  ``docker-compose.yml``)

.. _client-hub-todo-phase12:

Phase 12 — Ops Hardening + OpsInsights Override Pattern [COMPLETE]
======================================================================

Follow-on from the live multi-org upgrades on Clever Orchid and
Complete Dental Care, plus the regression where ``git reset --hard``
clobbered OpsInsights compose patches.

- [x] ``scripts/upgrade.sh`` — coordinated VPS upgrade runner
  (interactive by default, ``--yes`` for routine reruns) codifying
  the Migration-Strategy.rst Phase 5 deploy sequence
- [x] ``bootstrap-migrations.sh`` ``--via-docker`` flag for bundled
  VPSes whose MariaDB isn't published to the host
- [x] ``setup-opsinsights-tls.sh`` cert-aware step 1 (skips Caddy
  patch when cert already exists), netfilter-persistent install
  verification, ``--skip-ssl`` (not ``--ssl=0``) in the REQUIRE SSL
  test
- [x] New ``scripts/backfill-schema-tracker.sh`` — record pre-mig-018
  migrations as applied for old installs whose tracker is empty
- [x] New ``scripts/detect-drift.sh`` — sanity-check FK column types
  (canonical ``BIGINT UNSIGNED`` vs drifted ``int(11)``) before any
  upgrade that adds an FK column
- [x] OpsInsights override pattern: ``setup-opsinsights-tls.sh`` now
  writes ``docker-compose.opsinsights.yml`` (gitignored override)
  instead of mutating ``docker-compose.bundled.yml`` in place
- [x] ``upgrade.sh``, ``backup.sh``, ``uninstall.sh`` auto-include
  the override file when present
- [x] Both live VPSes migrated to the override pattern;
  ``docker-compose.bundled.yml`` is now canonical on both
- [x] Live upgrade procedure validated end-to-end on Clever Orchid
  (rebuild path, drift correction) and Complete Dental Care
  (standard path)

.. _client-hub-todo-phase13:

Phase 13 — Spam-Defense Framework (API-level) [COMPLETE]
======================================================================

Defense-in-depth spam filter at the Client Hub ingestion layer.
Every public-ish entry point inherits a 5-line guard via
``app.services.spam_filter_service.spam_check_or_raise`` — future
integrations (Zammad, marketing platform, scheduling, scraping,
etc.) plug in identically.

- [x] ``docs/Spam-Defense-Pattern.rst`` — full design contract +
  inheritance pattern documentation
- [x] Migration 023 — ``spam_patterns`` (operator-managed library),
  ``spam_events`` (rejection log for analytics + ETL),
  ``spam_rate_log`` (sliding-window rate-limit state)
- [x] Seeded 39 default patterns from the consumer-site filter
  lists (Complete Dental Care + Clever Orchid)
- [x] ``app/services/spam_filter_service.py`` — IntakePayload,
  SpamVerdict, ``spam_check_or_raise``, full pattern/event admin
  service surface
- [x] ``app/routers/spam.py`` — 6 admin endpoints + 1 source-key
  gated public endpoint for consumer-site pattern sync
- [x] Wired into ``POST /api/v1/contacts``,
  ``POST /api/v1/communications``, and
  ``POST /api/v1/webhooks/chatwoot``
- [x] False-positive correction path (operator marks event,
  pattern's ``false_positive_count`` bumps automatically)
- [x] Mode C (hard reject + dedicated ``spam_events`` log)
  preserves attack history without polluting primary tables
- [x] DB-driven patterns enable ops updates without code deploys;
  per-pattern hit/false-positive analytics built in
- [x] Multi-worker safe rate-limit via DB table (no Redis)
- [x] 13 new tests (114 total, was 101); ruff + rstcheck clean
- [x] Phone validation: US-only (10 digits, or 11 starting with 1)
  enforced framework-side; foreign country-code patterns block
  obvious offshore mills

.. _client-hub-todo-phase14:

Phase 14 — Spam-Defense Hardening: IP plumbing + pattern misses + audit gaps [COMPLETE]
=======================================================================================

Closing three issues uncovered by a real Hoff & Mazor cold-pitch
that landed in CDC prod on 2026-04-30. See
``docs/Spam-Defense-Pattern.rst`` (IP Capture & Trust Model,
Soft-Signal Audit Log) and the ``2026-05-01`` changelog entry.

- [x] uvicorn ``--proxy-headers --forwarded-allow-ips '*'`` in
  ``api/Dockerfile`` — Caddy's X-Forwarded-For is now trusted
- [x] Caddy ``header_up`` made explicit in ``Caddyfile``
- [x] New ``api/app/services/request_meta.py::extract_request_meta``
  helper — payload-supplied IP wins for source-key endpoints,
  fallback to ``request.client.host`` (private addresses dropped)
- [x] All ingest callsites use the helper (contacts.py,
  communications.py, webhooks.py)
- [x] ``CommCreate`` schema gains ``external_refs_json: dict | None``
- [x] ``IntakePayload`` carries ``user_agent``; rate-log + events
  rows persist it for forensics
- [x] IP-aware rate-limit via per-key thresholds in
  ``RATE_LIMIT_THRESHOLDS`` (email=1, email_body_hash=1, ip=5)
- [x] Migration 024 — 18 new B2B-pitch patterns covering the
  Hoff & Mazor body and similar variants
- [x] Migration 025 — ``source_id``/``user_agent`` columns on
  ``spam_rate_log``; ``user_agent`` on ``spam_events``
- [x] Migration 026 — ``spam_rate_log.occurred_at → DATETIME(6)``
  so same-second IP rows do not collide on the PK
- [x] Soft-signal audit path — single-phrase grazes write a
  ``spam_events`` row with ``rejection_reason='soft_signal'``;
  ``evaluate_intake`` now returns ``(verdict, soft_signal_match)``
- [x] ``scripts/backfill-spam-rate-log-ip.sql`` — idempotent
  one-shot to fix existing docker-bridge IP pollution from
  contemporaneous contact ``external_refs_json``
- [x] 10 new tests in ``api/tests/test_spam_ip_capture.py``;
  full suite is 125 tests, all green; ruff clean
- [x] Regenerate SDKs (``CommCreate.external_refs_json`` is a
  public-API change) — bumped to v0.2.0
- [x] Deploy + run backfill on Complete Dental Care VPS — live on
  v0.2.0; ``spam_rate_log`` IP key now shows ``43.246.220.151``
  (the real Hoff & Mazor IP) instead of the docker bridge peer
- [x] Deploy + run backfill on Clever Orchid VPS — live on
  v0.2.0; ``spam_rate_log`` IP key now shows ``172.59.217.107``
  (Mike Augustin's real IP) instead of the docker bridge peer

.. _client-hub-todo-phase15:

Phase 15 — Versioning & Fleet Readiness Foundations [IN PROGRESS]
======================================================================

The Client Hub will eventually run as dozens — possibly hundreds —
of single-tenant instances across different businesses. The release
discipline put in place now must scale to that without rewrites.
This phase covers the pieces that should be in place *long* before
the fleet scale arrives, sequenced smallest-first.

**v0.2.0 (2026-05-01) — done as part of this release:**

- [x] Single source-of-truth ``api/VERSION`` file
- [x] ``api/app/main.py`` reads VERSION at startup; FastAPI
  ``/openapi.json`` and ``/docs`` reflect it automatically
- [x] ``scripts/generate-sdks.sh`` stamps VERSION into Python +
  TypeScript SDK packages (``packageVersion`` arg)
- [x] ``scripts/generate-sdks.sh`` runs the generator container as
  the current uid:gid — no more root-owned files, no host sudo
- [x] First git tag: ``v0.2.0``
- [x] CHANGELOG.rst entries now lead with ``vX.Y.Z`` headings
  matching the git tag

**Near-term (next 1-2 releases):**

- [ ] ``scripts/release.sh`` — single command that bumps VERSION,
  regenerates SDKs, runs the test suite, commits, tags, and
  pushes (with ``--dry-run`` mode for review)
- [ ] Pre-commit / CI guard that fails when ``CHANGELOG.rst``
  has no entry for the current ``api/VERSION`` value
- [ ] PR template checklist item: "Migration is forward-only +
  idempotent (no destructive ALTERs without a soft-deprecation
  window)"
- [ ] Document the semver contract in
  ``docs/Versioning-Strategy.rst``: MAJOR = breaking API change
  (consumer SDK rebuild required); MINOR = additive endpoints /
  fields; PATCH = bugfix only, no schema or contract change

**Mid-term (when instance count > 5):**

- [ ] Per-instance ``/opt/client-hub/.channel`` file with values
  ``master`` (bleeding-edge), ``stable`` (latest ``v*`` tag), or
  a pinned tag like ``v0.4.2``
- [ ] ``scripts/upgrade.sh --target <ref>`` flag that ``git
  checkout``s a specific tag/branch instead of always
  fast-forwarding ``origin/master``
- [ ] ``scripts/autoupgrade.sh`` (cron-driven, opt-in per VPS)
  that polls GitHub for the channel's target ref, runs the
  upgrade with backup + smoke-test, and rolls back on failure
- [ ] Heartbeat / outcome reporting from each VPS to a
  central place (Brad's local follow-up system, or a future
  Client Hub control-plane endpoint)

**Long-term (fleet scale, 10+ instances):**

- [ ] Control-plane Client Hub instance with read-only access to
  fleet ``_schema_migrations`` + heartbeats; admin UI shows
  "29/52 instances are on v1.4.2; 23 are still on v1.3.x; 2
  failed last upgrade"
- [ ] SDK package publishing to PyPI / npm / Packagist (today
  the SDKs are committed in-tree — fine for 2 instances, not for
  hundreds)
- [ ] Provisioning automation (Terraform / Ansible) so a new
  instance is one command from "VPS exists" to "Client Hub
  running with auto-upgrade enabled"

.. _client-hub-todo-phase16:

Phase 16 — Phone E.164 standardization + Marketing-source attribution [COMPLETE]
================================================================================

Closing the two issues Steven flagged after v0.2.0. See
``docs/handoffs/cdc-v0.3.0.md`` and
``docs/handoffs/clever-orchid-v0.3.0.md`` and the ``v0.3.0``
changelog entry.

- [x] ``api/app/services/phone_utils.py::normalize_to_e164`` — single
  point of phone normalization; 28 unit tests
- [x] Pydantic ``field_validator`` on ``ContactCreatePhone.number``
  normalizes at ingestion (consumer sites need no change)
- [x] ``lookup_service.lookup_by_phone`` normalizes the path param
  before query; format-agnostic lookups verified
- [x] Migration 027 — backfill ``contact_phones`` and ``org_phones``
  to E.164 + DB-layer CHECK constraint
- [x] ``api/app/services/marketing_source_service.py`` — derivation
  rules + ``attach_codes`` writer
- [x] ``contact_service.create_contact`` runs derivation when the
  payload's ``marketing_sources`` is empty
- [x] New public endpoint ``GET /api/v1/marketing-sources``
  (source-key gated; mirrors ``/spam-patterns`` pattern)
- [x] ``scripts/backfill-marketing-sources.sql`` — idempotent SQL
  one-shot for existing contacts
- [x] KT handoff docs in ``docs/handoffs/`` for both consumer sites
- [x] 180 tests, all green; ruff + rstcheck clean
- [x] Deploy v0.3.0 to CDC + run backfill SQL — all 5 phones now
  E.164; all 5 contacts attributed to ``website``
- [x] Deploy v0.3.0 to Clever Orchid + run backfill SQL — all 17
  phones now E.164 (including ``(808) 256-8182`` → ``+18082568182``);
  all 17 contacts attributed to ``website``

.. _client-hub-todo-phase16-v0-3-1:

Phase 16 — v0.3.1 follow-ups [COMPLETE]
----------------------------------------------------------------------

- [x] Migration 028 — ``sources.domain`` backfill (idempotent,
  code-keyed). Applied on CDC; CDC's
  ``complete_dental_care_website`` row now has
  ``domain='completedentalcarecolumbia.com'``
- [x] ``scripts/cleanup-prod-test-pollution.sql`` — body-marker-keyed
  removal of three prod-pollution test contacts
- [x] Deploy v0.3.1 to CDC: contacts went 5 → 4 (Brad Stancel test
  row removed); domain populated
- [x] Deploy v0.3.1 to Clever Orchid: contacts went 17 → 15 (Mary T
  TEST-FROM-CLAUDE-S5 and "Repeat" rate-limit test rows removed)

**Discovered during the v0.3.1 deploy** — the CO instance has *no
named source row*. There is only the ``bootstrap`` source (the
install-time root key) and the consumer Next.js site has been
authenticating as that key, not a dedicated ``clever_orchid_website``
source. CDC was installed correctly with its own named source; CO
was not. Migration 028's ``UPDATE ... WHERE code='clever_orchid_website'``
was therefore a no-op on CO. This is an installation gap, not data
loss, but it muddies attribution (every CO contact has
``first_seen_source_id = bootstrap``).

.. _client-hub-todo-phase16-v0-3-2:

Phase 16 — v0.3.2 follow-ups [COMPLETE]
----------------------------------------------------------------------

- [x] Migration 029 — DELETE orphan ``bootstrap`` source rows
  (no api_keys, no contacts, no communications, no spam_events, no
  spam_rate_log references). Idempotent + fleet-safe
- [x] ``scripts/rename-bootstrap-source.sql`` — parameterized
  template for renaming an active ``bootstrap`` row in place
- [x] ``scripts/rename-bootstrap-clever-orchid.sql`` — committed
  CO-specific values for audit
- [x] Deploy v0.3.2 to CDC: orphan ``bootstrap`` dropped; only
  ``complete_dental_care_website`` remains
- [x] Deploy v0.3.2 to Clever Orchid: ``bootstrap`` renamed in
  place to ``clever_orchid_website`` (id=1 unchanged, all 15
  contacts and api_keys still resolve through the same FK); CO
  migration 029 was correctly a no-op because the row had dependents

.. _client-hub-todo-phase16-v0-3-3:

Phase 16 — v0.3.3 follow-ups [COMPLETE]
----------------------------------------------------------------------

- [x] ``scripts/install.sh`` now rejects ``bootstrap`` as the first
  source code and requires ``--first-source-code`` /
  ``--first-source-name`` / ``--first-source-domain`` /
  ``--first-source-type``. Future installs cannot reproduce the
  CO-shaped "bootstrap-as-runtime-identity" state.
- [x] ``scripts/install.sh`` now collects + INSERTs into
  ``business_settings`` (``--business-name`` required;
  type/timezone/currency/country/phone/email/website optional).
  Empty ``business_settings`` is now a deployment defect.
- [x] ``docs/Sources.rst`` (new) — discipline rule, bootstrap
  lifecycle, installer enforcement, key rotation, multi-source
  example. ``docs/data-model.rst`` references it from the
  ``sources`` section.
- [x] ``docs/data-model.rst`` brought fully current — sources,
  api_keys, spam_patterns, spam_events, spam_rate_log,
  v_events_by_source, _schema_migrations now first-class. Drift in
  contacts / communications / phone tables / marketing-source
  junction repaired.
- [x] ``scripts/seed-business-settings-cdc.sql`` +
  ``scripts/seed-business-settings-clever-orchid.sql`` — committed
  per-VPS values for the retroactive seed on pre-v0.3.3 instances
- [x] Deploy v0.3.3 to CDC: business_settings seeded (Complete
  Dental Care / dental / America/New_York / USD / US /
  https://completedentalcarecolumbia.com)
- [x] Deploy v0.3.3 to Clever Orchid: business_settings seeded
  (Clever Orchid / embroidery / America/New_York / USD / US /
  https://cleverorchid.com)

.. _client-hub-todo-phase16-v0-3-4:

Phase 16 — v0.3.4 follow-ups [COMPLETE]
----------------------------------------------------------------------

- [x] Fix ``Mapped[str] / String(10)`` ORM drift on five date
  columns (``orders.order_date``, ``orders.due_date``,
  ``invoices.invoice_date``, ``invoices.due_date``,
  ``payments.payment_date``). Models now declare
  ``Mapped[date] / Date`` to match the live ``DATE`` DDL on every
  running instance — no migration needed; storage was already
  correct. Discovered via stale EER export Steven extracted for the
  InvoiceNinja → Client Hub ETL planning.
- [x] Pydantic request/response schemas updated to use ``date`` /
  ``date | None`` for the same fields. OpenAPI now reports
  ``"format": "date"``; nullable fields use the
  ``anyOf [string-date, null]`` shape.
- [x] InvoiceNinja webhook ``payment_date`` now passes
  ``datetime.now(timezone.utc).date()`` instead of a pre-formatted
  string.
- [x] Regenerate Python, PHP, TypeScript SDKs against the updated
  spec; all stamped 0.3.4.
- [x] All 180 tests pass unchanged; ruff + rstcheck clean.
- [x] Deploy v0.3.4 to CDC via ``scripts/upgrade.sh --yes``: pre-HEAD
  ``27c48c9``, post-HEAD ``0ac5232``; backup
  ``backups/clienthub-20260505-172832.sql.gz``; 7/7 smoke tests
  passed; date columns confirmed still ``date`` post-upgrade.
- [x] Deploy v0.3.4 to Clever Orchid via ``scripts/upgrade.sh
  --yes``: same pre-/post-HEAD; backup
  ``backups/clienthub-20260505-172927.sql.gz``; 7/7 smoke tests
  passed; date columns confirmed still ``date`` post-upgrade.

.. _client-hub-todo-phase16-v0-3-5:

Phase 16 — v0.3.5 follow-ups [COMPLETE]
----------------------------------------------------------------------

- [x] Publish the TypeScript SDK to the private Verdaccio registry
  as ``@bradstancel/clienthub-sdk``. Patch
  ``scripts/generate-sdks.sh`` to post-process the generated TS
  ``package.json`` (name, repo, ``publishConfig``, ``files``,
  ``prepublishOnly``), remove the auto-generated ``.npmignore``
  (which excluded README.md), and replace the misleading
  auto-generated README with curated private-registry install
  instructions.
- [x] Add ``.github/workflows/publish-sdk.yml`` — tag-triggered
  publish workflow modeled on
  ``@bradstancel/website-scheduler``'s ``publish.yml``. Configure
  ``NPM_TOKEN`` GitHub repo secret with the brad publisher token
  (consumer token returned 403 on first publish; brad token
  authenticated correctly via ``curl /-/whoami`` returning
  ``{"username": "brad"}``).
- [x] First publish: ``@bradstancel/clienthub-sdk@0.3.5`` lands on
  Verdaccio (``~/docker/verdaccio/storage/@bradstancel/clienthub-sdk/``,
  36.2 kB tarball, sha ``643a7a67…``). ``npm view`` confirms
  ``dist-tags.latest=0.3.5``.
- [x] Deploy v0.3.5 to CDC API VPS via ``scripts/upgrade.sh --yes``:
  pre-HEAD ``0ac5232``, post-HEAD ``8988db0``; backup
  ``backups/clienthub-20260505-194633.sql.gz``; 7/7 smoke tests
  passed.
- [x] Deploy v0.3.5 to Clever Orchid API VPS via
  ``scripts/upgrade.sh --yes``: same pre-/post-HEAD; backup
  ``backups/clienthub-20260505-194650.sql.gz``; 7/7 smoke tests
  passed.
- [x] CDC consumer site (``completedentalcarecolumbia.com``)
  migrated from hand-rolled ``fetch()`` to the published SDK in
  commit ``0b46c9e``; deployed to droplet ``165.245.141.244``;
  reported back with feedback rolled into the v0.3.6 queue below.
- [x] Clever Orchid consumer site (``cleverorchid.com``) migrated
  to the published SDK in commit ``6524034``; deployed to droplet
  ``129.212.178.104``; uses only ``ContactsApi`` /
  ``CommunicationsApi`` / ``LookupApi`` (rest of SDK surface
  installed-but-unused).
- [x] ``docs/Cross-Project-Integration.rst`` rewritten SDK-first
  (the legacy hand-rolled ``fetch()`` reference module that misled
  CDC's pre-cutover state is now removed; recoverable from git
  history if needed). Added "Production Consumers" register so
  every consumer site, its source code, its pinned SDK version,
  its Client Hub VPS, and its cutover commit are tracked in one
  table.

.. _client-hub-todo-phase16-v0-3-6:

Phase 16 — v0.3.6 follow-ups [COMPLETE]
----------------------------------------------------------------------

- [x] ``api/app/schemas/lookup.py`` (new) — typed ``LookupResponse``
  with nested ``LookupMatch{Phone,Email,Order,Communication,ChannelPref}``.
  ``api/app/routers/lookup.py`` declares
  ``response_model=LookupResponse`` on both email + phone routes.
  OpenAPI now references ``#/components/schemas/LookupResponse``
  for the 200 responses; SDK ``lookupEmailApiV1LookupEmailEmailGet``
  now returns ``Promise<LookupResponse>`` instead of
  ``Promise<any>``. (Closes the defect both consumer sites flagged
  in their v0.3.5 cutover reports.)
- [x] ``scripts/generate-sdks.sh`` heredoc gained a "Timeouts and
  cancellation" section documenting the ``initOverrides`` pattern
  with a worked example. Both consumer-site Claude sessions had to
  reverse-engineer this from the SDK runtime in v0.3.5.
- [x] Live audit of both consumer sites' ``lib/client-hub.ts``:
  CDC at ``/home/brad/Sites/complete-dental-care-nextjs`` (commit
  ``0b46c9e``), Clever Orchid at
  ``/home/brad/Sites/clever-orchid-website`` (commit ``6524034``).
  Public surface identical; quality gaps each-way (CDC: lazy +
  cached config; CO: ResponseError parsing, extended UTM,
  trailing-slash strip).
- [x] ``docs/Cross-Project-Integration.rst`` reference module
  rewritten to embed the best-of-both canonical synthesis.
- [x] ``scripts/deploy-all-vpses.sh`` (new) + ``deploy/vpses.txt``
  (new) — multi-VPS deploy orchestrator. Reads the host list,
  runs ``./scripts/upgrade.sh --yes`` against each sequentially,
  verifies each via the public ``/api/v1/health`` and OpenAPI
  version, prints a summary table, aborts on first failure so
  remaining VPSes are untouched.
- [x] Bug caught in CI on the first v0.3.6 tag (``f5d73b8``):
  Pydantic ``Any | None`` in ``LookupMatchChannelPref.opt_in``
  produced an OpenAPI property with no ``type``, which
  openapi-generator's TypeScript template stamped as
  ``optIn?:  | null;`` and tried to call bare ``FromJSON()`` /
  ``ToJSON()`` helpers — TS compile error at publish time. Fixed
  by typing ``opt_in`` as ``str | None`` (matching the underlying
  ``contact_channel_prefs.opt_in_status`` ENUM column). v0.3.6
  retag forward to ``4176b92``; second publish run succeeded; no
  Verdaccio garbage left from the failed first run because the
  npm publish step is gated behind the build that failed.
- [x] First real run of ``scripts/deploy-all-vpses.sh``: rolled
  v0.3.6 to both API VPSes sequentially. Pre-HEAD ``8988db0`` →
  post-HEAD ``4176b92`` on each. Backups
  ``clienthub-20260505-211711.sql.gz`` (CDC) and
  ``clienthub-20260505-211823.sql.gz`` (CO). 7/7 smoke tests on
  each. Both report ``v0.3.6`` on ``/api/v1/health``.
- [x] Synthetic CDC live verification (pre-cut): POST
  ``/api/v1/contacts`` with a clearly-marked ``ZZ-Verification``
  payload via the SDK wire format proved end-to-end ingestion
  against production CDC; row landed with proper provenance
  (``first_seen_source_id=2`` correctly resolved); cleaned up
  with no residue (CDC contacts back to baseline of 4).
- [x] Handoff prompts for both consumer sites at
  ``docs/handoffs/cdc-v0.3.6.md`` and
  ``docs/handoffs/clever-orchid-v0.3.6.md`` — each spells out the
  specific gaps that site needs to close to converge on the
  canonical, plus the universal ``Promise<any>``-cast removal.

.. _client-hub-todo-phase16-v0-4-0:

Phase 16 — v0.4.0 follow-ups [COMPLETE]
----------------------------------------------------------------------

Driven by a 2026-05-06 production audit on
``client-hub-complete-dental-care.onlinesalessystems.com`` after a
SEO-pitch from "Davis Brown" (``davisseowebexpert@gmail.com``,
phone ``+12356895054`` — fake NANP area code 235, India IP
``106.219.155.100``) made it through to ``contacts`` (id 29) and
``communications`` (id 33). Investigation surfaced four real
defects, all fixed here.

- [x] Migration 030 — ``spam_events.peer_ip VARCHAR(45)`` column,
  indexes on ``remote_ip`` and ``peer_ip``. Splits canonical
  visitor IP from raw TCP peer so ``remote_ip`` is the queryable
  authoritative visitor IP and ``peer_ip`` records the proxy
  droplet for forensics.
- [x] Migration 031 — seed 5 new ``email_substring`` patterns
  (``seowebexpert``, ``webexpert``, ``webexpertsolution``,
  ``seoanalyst``, ``seospecialist``) and 7 new whitespace-tolerant
  ``phrase_regex`` patterns (``\\bdrop\\s+in\\s+website\\s+traffic\\b``,
  ``\\berrors\\s+and\\s+(the\\s+)?solutions\\b``,
  ``\\bimprove\\s+the\\s+performance\\s+and\\s+traffic\\b``, etc.)
  covering the SEO-outreach body shape. The ``\\s+`` tolerance is
  deliberate — the original migration-023 phrase used a literal
  space and was defeated by a double-space in the breakthrough
  body.
- [x] ``app/services/phone_utils.py`` — ``NANP_AREA_CODES``
  frozenset (~400 NPAs from `NANPA's public registry
  <https://nationalnanpa.com/reports/reports_npa.html>`_),
  ``is_valid_nanp_area_code(area)``, and
  ``extract_nanp_area_code(phone)`` helpers. Refresh annually.
- [x] ``app/services/spam_filter_service.py`` — new
  ``phone_invalid_areacode`` rule in ``evaluate_intake`` (between
  the digit-count check and the country-block patterns). Catches
  ``+12356895054`` which passed the digit count and which the
  ``+235`` country-block substring couldn't match because of the
  ``+1`` prefix. Pattern-level addition to ``IntakePayload``:
  ``peer_ip`` field; both ``_record_spam_event`` and
  ``_record_soft_signal`` now write ``spam_events.peer_ip``.
  ``_serialize_event`` exposes ``peer_ip`` separately in admin
  responses.
- [x] ``app/services/spam_filter_service.py`` —
  ``spam_check_or_raise`` gained a ``skip_email_rate_limit`` flag.
  The /communications endpoint sets it to True so the standard
  ``logConversion(contact + comm)`` consumer flow doesn't trip
  the email rate-limit (the contact-create has already written the
  email's rate-log row; counting the comm as a 2nd hit was
  blocking legitimate follow-ups). Email *pattern matching* still
  runs; only rate-limit keying skips the email keys.
- [x] ``app/services/request_meta.py`` — ``extract_request_meta``
  now returns a 3-tuple ``(canonical_ip, peer_ip, user_agent)``.
  Canonical IP is the public visitor IP (payload
  ``external_refs_json.ip_address`` if public → ``request.client.host``
  if public). Peer IP is the raw TCP peer kept for forensics
  (preserved even when private/loopback).
- [x] ``app/routers/communications.py`` — comm endpoint now looks
  up the parent contact's primary email and stored
  ``external_refs_json.ip_address`` and uses them as fallbacks.
  This means: (a) ``submitted_email`` is non-NULL on comm
  ``spam_events`` rows (was always NULL before) so email-substring
  patterns can fire on follow-ups, and (b) the canonical visitor
  IP propagates from the contact-create even when the comm
  payload itself doesn't carry one (consumer sites still on
  v0.3.6 SDK get correct IP forensics automatically).
- [x] ``app/routers/contacts.py`` and ``app/routers/webhooks.py`` —
  consume the new 3-tuple from ``extract_request_meta``; pass
  ``peer_ip`` into ``IntakePayload``.
- [x] Tests: ``tests/test_spam_filter_nanp.py`` (new, 31 cases) —
  ``extract_nanp_area_code`` + ``is_valid_nanp_area_code`` units
  + end-to-end NANP rejection;
  ``tests/test_communications_parent_lookup.py`` (new, 2 cases)
  — comm uses parent email + IP fallback, comm payload IP wins
  over fallback; ``tests/test_spam_ip_capture.py`` updated for
  the 3-tuple contract + new cases for peer_ip preservation;
  ``tests/test_spam_filter.py`` extended with the Davis Brown
  email-substring + body phrase-combo end-to-end rejections.
  Test count 180 → 217.
- [x] Handoff prompts: ``docs/handoffs/cdc-v0.4.0.md`` and
  ``docs/handoffs/clever-orchid-v0.4.0.md`` — both consumer sites
  need to (1) bump to ``@bradstancel/clienthub-sdk@^0.4.0``,
  (2) add ``externalRefsJson`` to the ``createCommunicationApiV1Communications``
  call in ``logConversion`` and ``appendCommunication``, and
  (3) mirror the ``NANP_AREA_CODES`` set into ``lib/spam-filter.ts``
  with an ``isValidNanpAreaCode`` helper wired into form-submit
  pre-validation. Adoption on each consumer's own schedule.
- [ ] **TODO:** confirm CDC and Clever Orchid each adopt the
  v0.4.0 handoff. After both confirm, update
  ``docs/Cross-Project-Integration.rst`` reference module to
  include ``externalRefsJson`` on the comm call (the canonical
  module currently reflects the v0.3.6 surface).
- [ ] **TODO:** annual NANPA registry refresh — re-pull
  ``NANP_AREA_CODES`` from the assignment registry and diff
  against the in-code list. Calendar reminder for 2027-05.
- [ ] **TODO:** post-deploy cleanup of the original CDC
  breakthrough — soft-delete ``contacts.id=29`` + leave
  ``communications.id=33`` intact for pattern-tuning forensics;
  insert a backdated ``spam_events`` row for the audit trail.

.. _client-hub-todo-v0-3-7-queue:

v0.3.7 queue (next time we cut a versioned release)
----------------------------------------------------------------------

Empty. Open suggestions land here as they arrive from the consumer
sites or from operational use of the v0.3.6 deploy orchestrator.

.. _client-hub-todo-v0-4-x-design:

v0.4.x design parking lot
----------------------------------------------------------------------

- [ ] **SDK ergonomic facade.** OpenAPI Generator's default method
  names are very long (e.g.,
  ``createContactEndpointApiV1ContactsPost``,
  ``lookupEmailApiV1LookupEmailEmailGet``). Both consumer sites
  worked around this by isolating SDK calls inside their own
  ``lib/client-hub.ts`` wrapper. A maintained
  ``@bradstancel/clienthub-sdk-facade`` package (or a
  ``client.contacts.create({...})``-style wrapper layer
  regenerated alongside the raw SDK) would let future consumers
  skip the wrapper module. Design conversation, not a quick patch
  — owns its own version cycle. Reported by CDC (#2).

.. _client-hub-todo-future:

Future — Planned Work
======================================================================

- [x] Deploy first production instance (Complete Dental Care VPS)
- [ ] Run cleanup-test-data.sh on production VPS
- [ ] Contact dedup/upsert endpoint (Section 6b — discuss with Brad)
- [ ] InvoiceNinja webhook integration (live)
- [ ] Chatwoot webhook integration (live)
- [ ] SIP/Phone CTI integration (live caller lookup)
- [ ] Zammad customer support integration
- [ ] Marketing campaign platform integration
- [ ] Scheduling form integration
- [ ] Web scraping / enrichment API integration
- [ ] Online booking portal (prospect self-registration)
- [x] Expose API via Caddy with auto-TLS (bundled compose)
- [x] Automated database backups (nightly cron)
- [ ] Monitoring and alerting
- [ ] Data retention / PII purge automation
- [ ] Rate limiting on admin endpoints
