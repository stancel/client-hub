.. _client-hub-todo:

######################################################################
Client Hub — TODO
######################################################################

.. _client-hub-todo-phase1:

Phase 1 — Data Model Design [COMPLETE]
======================================================================

- [x] Design 3NF data model (initial: 31 tables + 2 views;
  current after Phases 8–9: 34 tables + 3 views)
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
- [ ] Deploy + run backfill on Complete Dental Care VPS
- [ ] Deploy + run backfill on Clever Orchid VPS

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
