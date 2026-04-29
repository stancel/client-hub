.. _client-hub-changelog:

######################################################################
Client Hub — Changelog
######################################################################

.. _client-hub-changelog-2026-04-29:

2026-04-29 — Spam-Defense Framework (API-level)
==========================================================================

Defense-in-depth spam filter at the Client Hub API ingestion layer.
Three sites (Complete Dental Care, Clever Orchid, this Client Hub
itself) now share the same canonical pattern library, with Client
Hub as the single source of truth that consumer sites pull from.

**Mode:** hard reject (HTTP 422) at ingestion, with every rejection
logged to a dedicated ``spam_events`` table for analytics + ETL.
Primary entity tables (``contacts``, ``communications``, ``orders``,
etc.) stay clean — no ``is_spam`` columns to filter against, no FK
pollution risk. Attack history is fully preserved and queryable.

**Migration 023 (``spam_patterns_and_events.sql``):**

- ``spam_patterns`` — operator-managed pattern library. Five
  ``pattern_kind`` values: ``email_substring``, ``full_email_block``,
  ``url_regex``, ``phrase_regex``, ``phone_country_block``.
  Per-pattern ``hit_count``, ``last_hit_at``, ``false_positive_count``
  for built-in analytics.
- ``spam_events`` — every rejection with denormalized
  ``matched_pattern_text`` (survives pattern deletion),
  ``rejection_reason``, redacted ``payload_json``, ``remote_ip``,
  ``submitted_email/phone/body_hash``, ``endpoint``,
  ``integration_kind``, ``occurred_at``, ``was_false_positive``.
- ``spam_rate_log`` — sliding-window rate-limit state (10-min
  window). Multi-worker safe via DB; no Redis dependency added.
- Seeded 39 default patterns from the consumer-site filter lists
  (the same regex/substring families that catch the SEO outreach
  mills, Calendly lead-gen pitches, foreign country-code phones).

**API surface (``/api/v1`` — 36 paths now, was 30):**

- ``GET /spam-patterns`` — source-key gated; consumer sites fetch
  this at build time to keep their server-side filter in sync with
  Client Hub's canonical list. One source of truth fans out to
  every Web Factory site on next deploy.
- ``GET/POST/PUT/DELETE /admin/spam-patterns`` — root-key, full
  pattern CRUD with metadata visibility.
- ``GET /admin/spam-events`` — root-key, paginated rejection log
  with filters by endpoint / integration_kind / rejection_reason /
  submitted_email / was_false_positive.
- ``GET /admin/spam-events/stats`` — root-key, attack analytics
  (hits per endpoint, hits per pattern with false-positive rates,
  top attacker IPs).
- ``POST /admin/spam-events/{uuid}/mark-false-positive`` —
  root-key, marks an event as a false positive and bumps the
  matched pattern's ``false_positive_count``.

**Reusable inheritance pattern:**

Every protected endpoint declares an integration adapter
(``_extract_intake(body, request)``) plus a one-line
``await spam_check_or_raise(...)`` call before the DB write. New
integrations (Zammad, marketing platforms, scheduling, scraping)
plug in with five lines of glue and inherit all current and future
spam patterns + rate limiting + observability automatically.

**Wired in this release:**

- ``POST /api/v1/contacts`` — web_form integration_kind
- ``POST /api/v1/communications`` — web_form integration_kind
- ``POST /api/v1/webhooks/chatwoot`` — webhook integration_kind
  (public-facing widget surface)

**Code:**

- New ``app/models/spam.py`` — SQLAlchemy models for
  ``SpamPattern``, ``SpamEvent``. ``spam_rate_log`` accessed via
  raw SQL for hot-path performance.
- New ``app/schemas/spam.py`` — Pydantic shapes for public read,
  admin CRUD, event list, stats payload.
- New ``app/services/spam_filter_service.py`` — the engine.
  ``IntakePayload``, ``SpamVerdict``, ``spam_check_or_raise``,
  pattern/event admin helpers. Validates regex on pattern create.
  Phone digit-count check (US-only, exactly 10 digits or 11
  starting with 1) is framework-level, not pattern-driven.
- New ``app/routers/spam.py`` — public + admin routers, registered
  in ``app/main.py``.
- ``contacts.py`` / ``communications.py`` / ``webhooks.py`` —
  thin adapters and one-line guard calls.

**Tests:** 13 new tests in ``tests/test_spam_filter.py``
(public read auth, admin pattern CRUD with regex validation,
rejection paths via ``POST /contacts`` for each pattern kind,
clean-payload acceptance, event listing/stats, false-positive
mark-and-counter-bump). 114 tests total (was 101). Pytest +
ruff + rstcheck all clean.

**Test-isolation fix:** ``tests/conftest.py`` now includes a
session-scope fixture that wipes ``spam_rate_log`` and
``spam_events`` at session start. The rate-limit log persists
across pytest runs by design (durable, multi-worker-safe in
production), but that meant a clean-payload test from a prior
run could rate-limit the same submission within the 10-min
window. The fixture gives every run a clean slate while leaving
the seeded ``spam_patterns`` library intact.

**Documentation:**

- New ``docs/Spam-Defense-Pattern.rst`` — full design doc,
  including inheritance pattern for future integrations.
- ``CLAUDE.md``, ``README.rst`` — synced with new endpoint counts
  (36 paths, was 30), table counts (39, was 36), test counts
  (114, was 101), router count (12, was 11), migration count
  (22 numbered files, was 21), docs/ count (18 files, was 17).
- TODO Phase 13 entry tracking everything above.

**SDK regeneration deferred to CI:** the local generate-sdks.sh
hit the same root-owned-files issue as the 2026-04-24 multi-org
release; the CI ``generate-sdks`` job on master merge regenerates
fresh.

.. _client-hub-changelog-2026-04-24b:

2026-04-24 — Live VPS Upgrades + Operational Hardening
==========================================================================

Follow-on to the morning's multi-org work (2026-04-24a). The
multi-org release was deployed to both live VPSes
(Clever Orchid Embroidery and Complete Dental Care Columbia) and
the upgrade exposed three latent issues that all got fixed and
codified for the next release.

**Live deployments:**

- **Clever Orchid** (``client-hub.cleverorchid.com`` /
  ``165.245.130.39``) upgraded via the rebuild path. ``int(11)``
  drift DB-wide (root cause unknown — predates current
  ``install.sh``) made the canonical FK in migration 019
  uncreatable, so the schema was rebuilt from migrations 001-022
  and data restored from a data-only dump. 15 contacts, 17
  communications, 1 affiliation backfilled; zero data loss.
- **Complete Dental Care** (``165.245.141.244``) upgraded via the
  standard path; no drift, ``_schema_migrations`` properly
  populated. 21 contacts, 24 comms, 4 orders preserved.
- **OpsInsights setup completed on Complete Dental Care:** TLS
  cert mounted from Caddy's Let's Encrypt directory, port 3306
  published, iptables ``DOCKER-USER`` allowlist for
  ``52.72.248.4`` and ``52.207.33.249``, ``opsinsights_ro`` user
  with ``REQUIRE SSL``.

**OpsInsights regression on Clever Orchid (root cause + fix):**

The rebuild's ``git reset --hard origin/master`` step reverted
``docker-compose.bundled.yml`` to canonical, wiping the in-place
patches that ``setup-opsinsights-tls.sh`` had applied on
2026-04-18 (port publish, TLS cert mount,
``--ssl-cert``/``--ssl-key`` flags). The recreated MariaDB
container came up without OpsInsights connectivity. The
``opsinsights_ro`` user, GRANTs, iptables rules, and cert
staging directory all survived — only the compose plumbing was
gone. Refactored to a durable override pattern (below) so the
next upgrade doesn't repeat this.

**Refactor — OpsInsights to ``docker-compose.opsinsights.yml`` override:**

- ``scripts/setup-opsinsights-tls.sh`` no longer edits
  ``docker-compose.bundled.yml`` in place. Instead it writes a
  gitignored ``docker-compose.opsinsights.yml`` carrying only the
  OpsInsights additions (port publish, cert mount, ssl flags).
  Docker Compose merges it via
  ``docker compose -f bundled.yml -f opsinsights.yml``.
- Migration logic detects legacy in-place patches and reverts
  them via ``.bak-pre-opsinsights`` or ``git checkout`` before
  writing the override.
- ``scripts/upgrade.sh``, ``scripts/backup.sh``,
  ``scripts/uninstall.sh`` all auto-include the override file
  when present, so every ``docker compose`` invocation matches
  the running container set.
- Both live VPSes migrated to the override pattern. Their
  ``docker-compose.bundled.yml`` is now canonical (matches
  ``origin/master``); OpsInsights state lives only in the
  gitignored override file. Existing ``opsinsights_ro``
  passwords preserved (no ``--rotate-password``).

**New ops scripts:**

- ``scripts/upgrade.sh`` — coordinated VPS upgrade runner that
  codifies the Migration-Strategy.rst Phase 5 deploy sequence.
  Interactive by default; ``--yes`` skips pauses for routine
  reruns. Prints rollback command line at the end with the
  exact backup path and prior HEAD.
- ``scripts/detect-drift.sh`` — exits 0 when ``contacts.id`` is
  the canonical ``BIGINT UNSIGNED``, exit 1 otherwise. Run before
  any upgrade that adds an FK column.
- ``scripts/backfill-schema-tracker.sh`` — one-shot helper to
  populate ``_schema_migrations`` on installs older than mig 018
  (the migration that introduced the tracker). Without this,
  ``bootstrap-migrations.sh`` re-attempts every migration from
  001 onwards and trips on non-idempotent ``ALTER`` in mig 013.

**``bootstrap-migrations.sh`` ``--via-docker`` flag:**

Bundled VPS compose files don't publish MariaDB on 3306 until
OpsInsights setup runs. The host ``mariadb`` client therefore
can't reach ``127.0.0.1:3306`` and the bootstrap script silently
exited after the header. New flag bypasses the published port:
``--via-docker clienthub-mariadb`` runs every mariadb command
via ``docker exec -i``.

**``setup-opsinsights-tls.sh`` smaller fixes:**

- Step 1 now checks the Caddy cert directory before grepping the
  Caddyfile for a literal ``HOSTNAME {`` block. Fixes the false
  positive on installs that use the ``{$DOMAIN}`` template form
  (Complete Dental Care).
- Step 4 ``iptables-persistent`` install now verifies
  ``netfilter-persistent`` actually ended up on PATH. The
  previous ``dpkg -l`` check returned 0 even for packages in
  ``un`` state, so a silent install failure manifested later as
  ``netfilter-persistent: command not found``.
- Step 8 verification switched from ``--ssl=0`` (a soft hint
  that can still negotiate TLS in modern MariaDB clients) to
  ``--skip-ssl`` (the actual disable). Eliminates the false
  positive "REQUIRE SSL not enforced" warning.

**Doc sync:**

CLAUDE.md, README.rst, docs/architecture.rst, TODO.rst headline
numbers refreshed against reality (36 tables + 3 views, 30
endpoint paths, 101 tests across 18 files, 12 shell scripts, 17
docs/ files). New TODO Phase 12 entry tracks all of the above.

.. _client-hub-changelog-2026-04-24a:

2026-04-24 — Multi-Org Refactor + Schema Name Standardization
==========================================================================

Two coordinated changes landed in one release: (1) multi-org
affiliations via a proper junction table (replacing the denormalized
``contacts.organization_id`` cached pointer), and (2) schema-name
standardization on ``clienthub`` across every environment.

**Breaking changes (clean break, no dual versioning):**

- ``/api/v1/contacts`` — ``organization_uuid`` removed from
  create/update requests and responses. Use the new
  ``affiliations`` list instead. Responses now carry
  ``primary_organization_uuid`` (computed from the
  ``is_primary=true`` affiliation) and a nested
  ``affiliations[]`` list.
- ``/api/v1/contacts/{uuid}/summary`` — ``organization`` replaced
  by ``primary_organization_uuid``, ``primary_organization_name``,
  ``primary_role_title``, ``primary_department``.
- Contact phone/email/address create accepts new optional
  ``affiliation_uuid`` to scope work-specific rows.
- ``v_contact_summary`` view rewritten (migration 021) —
  ``organization_id`` column gone; ``organization_name`` now
  sourced from the primary affiliation; new columns
  ``primary_role_title``, ``primary_department``.
- Local Cybertron development DB renamed: ``dev_schema`` →
  ``clienthub`` (backup saved at
  ``backups/dev_schema_pre_rename_20260424_123810.sql``). Sister
  ``~/docker/mariadb/`` project standardized on same name.
  CI test database renamed ``test_schema`` →
  ``clienthub_test`` in ``.github/workflows/ci.yml``.

**Migrations:**

- **019** ``contact_org_affiliations.sql`` — Junction table +
  ``seniority_levels`` lookup (exec/senior/mid/junior/intern/unknown)
  + backfill from ``contacts.organization_id`` + generated-column
  partial-unique index ``ux_coa_one_primary`` enforcing at most
  one primary affiliation per contact at the DB level.
- **020** ``contact_details_affiliation_fk.sql`` — Nullable
  ``affiliation_id`` FK on contact_phones, contact_emails,
  contact_addresses (``ON DELETE SET NULL``).
- **021** ``drop_contacts_organization_id.sql`` — Drops the
  legacy FK + column; rewrites ``v_contact_summary`` to source
  organization info from the primary affiliation.
- **022** ``primary_uniqueness_details.sql`` — Generated-column
  partial-unique indexes on all three detail tables enforcing
  "at most one primary per contact" at the DB level (previously
  service-layer-only).

All four migrations are idempotent (``CREATE TABLE IF NOT EXISTS``,
``ADD COLUMN IF NOT EXISTS``, ``INSERT ... ON DUPLICATE KEY UPDATE``,
INFORMATION_SCHEMA-guarded dynamic SQL for constraints, ``NOT EXISTS``
guarded backfills).

**API surface additions:**

- ``GET /api/v1/contacts/{uuid}/affiliations`` —
  list (with ``active_only`` filter)
- ``POST /api/v1/contacts/{uuid}/affiliations`` — create
- ``PUT /api/v1/contacts/{uuid}/affiliations/{affiliation_uuid}`` —
  update (with primary promotion auto-demoting the current primary)
- ``DELETE /api/v1/contacts/{uuid}/affiliations/{affiliation_uuid}`` —
  hard-delete (auto-promotes another active affiliation to primary
  when the current primary is deleted, if any remain)

**Invariant model:**

- "At most one primary per contact" is now DB-enforced across
  ``contact_org_affiliations``, ``contact_phones``,
  ``contact_emails``, ``contact_addresses`` via virtual generated
  columns (``is_primary_key = IF(is_primary, 1, NULL)``) plus
  composite UNIQUE indexes. NULL doesn't participate in UNIQUE on
  InnoDB/MariaDB, so non-primary rows are unconstrained.
- "At least one primary when any rows exist" is service-layer
  enforced (affiliations only — phone/email/address "at least one"
  is advisory).
- Combined semantics: exactly-one-primary when any rows exist,
  without needing ``BEFORE`` triggers.

**Documentation:**

- New ``docs/Migration-Strategy.rst`` playbook codifying the
  idempotent-migration + TDD-first + bundled-PR pattern for future
  schema refactors.
- ``docs/data-model.rst`` fully updated; also synced the
  previously-stale 014–018 gaps in the Complete Table List
  (entity/junction/lookup/system counts).
- ``docs/api-design.rst`` — new Breaking Changes section at the top
  + Contact Affiliations endpoint group.

**Testing:**

- 12 new tests in ``tests/test_contact_affiliations.py`` covering
  list/create/update/delete, demote-previous-primary, promote-on-delete,
  inline affiliation on ``POST /contacts``, and the contact summary's
  new primary-org fields.
- Total: **101 passing** (was 89).

**SDK regeneration:**

Local regen was blocked by root-owned files in ``sdks/python/docs/``
from a prior container-based generate. CI (``generate-sdks`` job on
master branch) regenerates cleanly on merge. One-time followup:
``sudo chown -R brad:brad sdks/`` on Cybertron to unblock future
local regens.

**Rollout / operations:**

- Cybertron local Cybertron DB cutover executed:
  stop client-hub-api → backup → create ``clienthub`` → restore
  dump → update ``.env`` → restart → smoke test → drop
  ``dev_schema``. Row counts match pre-rename.
- Complete Dental Care VPS already uses ``clienthub`` per the
  bundled deployment pattern — no change needed there.

.. _client-hub-changelog-2026-04-22:

2026-04-22 — README: Prominent One-Line Installer Section
==========================================================================

The one-line ``curl | sudo bash`` installer (``scripts/install.sh``,
shipped in Phase 8) was discoverable only from ``CLAUDE.md`` and the
``docs/Deployment.rst`` guide — there was no mention in ``README.rst``,
which is the first thing anyone provisioning a new VPS looks at. Fixed.

- ``README.rst`` — New **One-Line Installer** chapter placed directly
  after the Overview (above Quick Info) so it is the first actionable
  thing after the project intro. Includes the interactive one-liner,
  the non-interactive form with all flags, and a flag reference table
  (``--mode``, ``--domain``, ``--admin-email``, ``--first-source-code``,
  ``--first-source-name``, ``--sdks``, ``--include-seed-data``,
  ``--install-dir``, ``--non-interactive``). Points to
  ``scripts/smoke-test.sh`` for post-install verification and
  ``docs/Deployment.rst`` for the full guide.
- Fixed stray "Embro idery" typo in the Overview paragraph.
- ``rstcheck --report-level warning README.rst`` — clean.

Installer URL still pointing at
``raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh``
per Brad — the repo will move eventually but not yet.

.. _client-hub-changelog-2026-04-18b:

2026-04-18 — OpsInsights TLS Fix Verified; Script Defaults to REQUIRE SSL
==========================================================================

Follow-up to the morning's 2026-04-18a entry. Between then and the end
of the day, Brad patched the OpsInsights ADOdb PDO SSL bug, deployed to
production, and verified the fix end-to-end against the Clever Orchid
Client Hub. The MariaDB general log captured 10+ TLS-encrypted
connections from OpsInsights egress IPs across both the production
SaaS path (``52.207.33.249``, AWS NAT Gateway) and the operator path
(``52.72.248.4``, OpenVPN) with zero plaintext attempts. ``REQUIRE SSL``
has been restored on the ``opsinsights_ro`` user. Full defense-in-depth
(IP allowlist + TLS + MariaDB auth + read-only grants) is back in force.

Script + docs updated to reflect the new reality:

- ``scripts/setup-opsinsights-tls.sh`` — ``REQUIRE_SSL`` default flipped
  from ``false`` to ``true``. Flag renamed: ``--require-ssl`` now a no-op
  (kept for back-compat); new ``--no-require-ssl`` for the rare case of
  onboarding against an older OpsInsights build. Verification step
  inverted accordingly — plaintext login must now be REJECTED in the
  default path.
- ``docs/OpsInsights-Direct-TLS-Plan.rst`` — Status line updated from
  "deviations from plan" to "fully verified". Old "Deviation — REQUIRE
  SSL dropped (interim)" section renamed to "History" and rewritten as
  a chronological narrative (interim drop → fix deployed → REQUIRE SSL
  restored → verified by client-side SSL-off test).
- ``docs/OpsInsights-Setup-Prompt.rst`` — Default run invocation no
  longer carries an interim caveat. Flag description inverted. Added
  an IP-role note (``52.207.33.249`` = NAT Gateway, ``52.72.248.4`` =
  OpenVPN) — these were originally labeled reversed in Brad's
  ``connect.opsinsights.com`` public docs, corrected after live
  traffic observation.
- IP role labels corrected throughout all three RST docs.

Clever Orchid Client Hub connection is now production-ready and fully
encrypted in transit. First customer Client Hub deployment closed out.

.. _client-hub-changelog-2026-04-18a:

2026-04-18 — OpsInsights SaaS Connection: Direct MySQL/TLS + IP Allowlist
==========================================================================

First real SaaS-integration pattern proven end-to-end against the
live Clever Orchid Client Hub VPS (``client-hub.cleverorchid.com``
/ ``165.245.130.39``). Two reusable integration plans documented,
one automation script written, first customer onboarded.

- New doc ``docs/OpsInsights-Direct-TLS-Plan.rst`` — the chosen
  connection pattern: MariaDB published on 3306 with a Let's
  Encrypt TLS cert (acquired via Caddy for a second vhost), iptables
  DOCKER-USER chain restricts inbound to the two OpsInsights exit
  IPs (``52.72.248.4`` / ``52.207.33.249``), read-only MariaDB user
  per customer. Full "As Implemented" section documents the actual
  deployed state on Clever Orchid, including the two production
  deviations: global ``require_secure_transport`` not set (would
  break the internal FastAPI connection), and ``REQUIRE SSL`` on
  the user was dropped at runtime because OpsInsights cannot
  negotiate TLS on MySQL connections due to a bug in its hardcoded
  ADOdb PDO driver. See the Deviation section for the full bug
  writeup and the two-line patch for the future OpsInsights
  modernization pass.
- New doc ``docs/OpsInsights-SSH-Tunnel-Plan.rst`` — the alternative
  integration pattern for read/write enrichment work. Preserved as
  a reference plan for when CTI ingest and InvoiceNinja join
  workflows need to write back to Client Hub. Not implemented yet.
- New doc ``docs/OpsInsights-Setup-Prompt.rst`` — the Knowledge
  Transfer prompt for future customer onboarding. Explains what the
  setup script does and why, prerequisites, run invocation,
  verification procedure on both sides, operational notes (cert
  renewal, rotation, revert), and the security model with
  compromise scenarios. Written so a fresh Claude Code session
  opened in ``/opt/client-hub/`` can execute the work end-to-end.
- New script ``scripts/setup-opsinsights-tls.sh`` — parameterized,
  idempotent automation of the whole flow. Adds the Caddyfile vhost,
  waits for ACME, stages the cert, patches
  ``docker-compose.bundled.yml`` for the 3306 publish + TLS mount,
  installs ``iptables-persistent`` and adds ``DOCKER-USER`` allow
  rules, recreates the MariaDB container, creates the read-only
  user, writes and emits credentials. Flags: ``--hostname``,
  ``--allow-ip`` (repeatable), ``--install-dir``, ``--mariadb-user``,
  ``--require-ssl`` (opt-in; default off pending OpsInsights fix),
  ``--rotate-password``, ``--dry-run``, ``--non-interactive``.
- First production customer: Clever Orchid Embroidery. 11 contacts
  / 13 communications as of onboarding. OpsInsights SaaS dashboard
  integration pending verification (the user retries the connection
  on the OpsInsights side before this commit is pushed).

.. _client-hub-changelog-2026-04-11f:

2026-04-11 — Documentation Sync Pass
======================================================================

End-of-day ``bring-repo-in-sync`` audit. No code changes; updated
docs to match current reality after Phases 8, 9, and 10 shipped
in rapid succession.

- ``CLAUDE.md`` — corrected counts (34 tables + 3 views;
  28 endpoint paths; 89 tests / 17 files; 17 prod migrations +
  1 dev); added Admin endpoint category (sources, api-keys,
  events); added note on the ``external_refs_json`` payload
  contract; expanded directory tree with bundled compose files
  and all 8 scripts; added ``v_events_by_source`` to views
  section; added production VPS URL and installer one-liner to
  Key Commands.
- ``README.rst`` — same count corrections in Quick Info,
  architecture diagram, Database Schema section, and Testing
  section; added Admin endpoint rows to API table; added
  ``api_keys``, ``sources``, ``_schema_migrations`` to the entity
  / lookup / system table lists; added ``v_events_by_source``;
  fully rewrote Project Structure tree to list all current
  files, directories, scripts, and docs.
- ``TODO.rst`` — noted current vs. initial counts in Phase 1,
  2, and 5 (schema grew from 31/2 to 34/3; tests from 63 to 89;
  paths from 23 to 28); added Phase 10 section for the
  ``external_refs_json`` fix.
- Claude Code project memory ``project_vision.md`` — updated
  phase list through Phase 10, reflected current counts, added
  notes on live VPS and the payload contract reference.

.. _client-hub-changelog-2026-04-11e:

2026-04-11 — Document external_refs_json Payload Contract
======================================================================

Documentation-only follow-up after the external_refs_json fix was
verified on the live dental care VPS. The server-side round-trip
proved the fix works, but surfaced that the dental care caller is
sending a thin payload and that ``booking.cancelled`` overwrites
``booking.created``.

- ``docs/Cross-Project-Integration.rst`` — added new section
  "external_refs_json Payload Contract" with the canonical JSON
  shape, a "don't shadow — merge" rule for scheduler update
  hooks, and a checklist new Web Factory sites (Clever Orchid,
  etc.) must satisfy before going live.
- ``docs/Dental-Care-Payload-Fix-Prompt.rst`` — new handoff prompt
  for the dental care Next.js session, covering: capturing
  request headers in the booking form server action, enriching
  ``extra`` with scheduler event details, fixing the
  ``booking.cancelled`` overwrite by appending a communication
  row instead of re-upserting the contact, and investigating the
  separate frontdesk cancellation email bug.

No code changes. Client-hub server side is unchanged from
``fa6bf2d``.

.. _client-hub-changelog-2026-04-11d:

2026-04-11 — Fix external_refs_json Data-Loss Bug
======================================================================

Fix for silent data loss on every ``POST /api/v1/contacts``
(and the same issue on Organization and Order create/update):

- **Root cause:** ``external_refs_json`` existed on the ORM models
  for Contact, Organization, and Order but was not declared on any
  Pydantic request schema, so FastAPI silently stripped the field
  from every create/update body before it reached the service
  layer. Every row created via the API had ``external_refs_json``
  NULL even when the client sent rich metadata.
- **Fix (Contact):** added
  ``external_refs_json: dict[str, Any] | None`` to
  ``ContactCreate`` / ``ContactUpdate``; GET/POST/PUT responses now
  return the parsed dict. Service layer serializes dict → JSON
  string on write, deserializes defensively on read (malformed
  rows log a warning and return ``None`` instead of 500).
- **Fix (Organization, Order):** same field added to their inline
  create/update Pydantic schemas; create and GET responses now
  round-trip the value.
- **Tests:** 7 new round-trip tests across
  ``test_contacts.py``, ``test_organizations.py``, and
  ``test_orders.py`` (with value, without value, update,
  deep-nested). ``pytest`` now reports **89 passed** (was 82).
- **Impact:** unblocks the dental care integration's
  ``lib/client-hub.ts`` payload (source_page, ip_address,
  user_agent, nested ``extra`` with appointment_id / service_name
  / staff_name / start_date / total_price) and future Eaglesoft
  sync metadata. Client-side code needs no changes.

.. _client-hub-changelog-2026-04-11c:

2026-04-11 — Post-Deployment Fixes and Hardening
======================================================================

Fixes from first real VPS deployment on
``client-hub-complete-dental-care.onlinesalessystems.com``:

- **Smoke test fix:** removed ``curl -sf`` (which suppresses 4xx
  status codes); now accepts 401 or 403 for unauthenticated access
- **Seed data separation:** moved ``012_seed_test_data.sql`` to
  ``migrations/dev/``; production installs no longer get test data.
  Use ``--with-seed-data`` flag for dev/CI. Updated CI workflow.
- **Cleanup script:** ``scripts/cleanup-test-data.sh`` for removing
  test data from already-contaminated production instances
- **Installer hardening:** DNS pre-flight check for TLS domains,
  ``--include-seed-data`` flag, ``docker-compose.override.yml.example``
  for OpsInsights access
- **Uninstall safety:** preserves ``.env`` and ``.install-summary``
  to ``/root/client-hub-saved/`` before deletion
- **Lookup fix:** phone and email lookup now return ALL contact
  phones and emails (not just the matched one)
- **Admin events endpoint:** ``GET /api/v1/admin/events`` with
  source_code, channel_code, date range filters (root-key-only)
- **82 tests passing** (was 78)

.. _client-hub-changelog-2026-04-11b:

2026-04-11 — Multi-Source Attribution + One-Line Installer
======================================================================

Major implementation based on Installation-Implementation-Prompt.rst:

**Goal A — One-Line Installer:**

- ``scripts/install.sh`` — Ollama-style ``curl|bash`` for Ubuntu/Debian
- ``scripts/uninstall.sh``, ``backup.sh``, ``bootstrap-migrations.sh``,
  ``smoke-test.sh``, ``generate-api-key.sh``
- ``docker-compose.bundled.yml`` (MariaDB + API + Caddy with auto-TLS)
- ``docker-compose.bundled-nodomain.yml`` (MariaDB + API, port 8800)
- ``Caddyfile`` with auto Let's Encrypt

**Goal B — Multi-Source Attribution:**

- Migrations 014-018: ``sources``, ``api_keys`` tables,
  ``first_seen_source_id`` on contacts, ``source_id`` on
  communications, cross-project channel_types (10 new Web Factory
  event codes), ``v_events_by_source`` view, ``_schema_migrations``
  tracking table
- New auth middleware: resolves X-API-Key to SourceContext (root key
  or per-source key)
- Admin router: CRUD for sources + API keys (root-key-only)
- Auto-stamps source_id on contact/communication creation
- Schema now: 34 tables + 3 views

**Goal C — Cross-Project Integration:**

- ``docs/Multi-Source.rst`` — sources vs marketing_sources
- ``docs/Deployment.rst`` — one-liner install guide
- ``docs/Cross-Project-Integration.rst`` — reference lib/client-hub.ts
- ``docs/Data-Privacy.rst`` — PII handling policy
- ``docs/Upgrade.rst`` — upgrade and key rotation guide

**Tests:** 78 passing (63 original + 15 new) across 16 test files

.. _client-hub-changelog-2026-04-11:

2026-04-11 — Full Documentation Refresh
======================================================================

- Rewrote README.rst to reflect complete project state: all 7 phases
  done, 23 endpoints, 63 tests, 3 SDKs, CI/CD pipeline, full
  architecture diagram, endpoint table, project structure tree
- Rewrote CLAUDE.md with current container info, all key commands,
  troubleshooting for the live API, SDK generation, CI/CD details
- Updated architecture.rst with live container layout and integration
  patterns (webhook, lookup, CRUD, direct SQL)
- All docs now accurately reflect the running system

.. _client-hub-changelog-2026-04-05h:

2026-04-05 — All API Endpoints Complete: 63 Tests, 23 Paths
======================================================================

- Implemented remaining routers: organizations, orders, invoices,
  payments, communications, webhooks (InvoiceNinja + Chatwoot),
  business settings
- 63 tests passing across 13 test files in 0.76 seconds
- 23 endpoint paths live on port 8800
- Full order lifecycle: create → add items → change status → invoice
  → record payments (auto-updates balance and status)
- Webhook handlers: InvoiceNinja payment sync, Chatwoot message
  identification and communication logging
- Container rebuilt and verified with curl

.. _client-hub-changelog-2026-04-05g:

2026-04-05 — Phase 5: API Server Live with 30 TDD Tests
======================================================================

- FastAPI server running in Docker on port 8800 (my-main-net)
- 30 tests passing across 6 test files (TDD, real DB)
- Implemented endpoints: health, phone/email lookup, contacts CRUD,
  conversion, marketing opt-outs, preferences, contact summary
- API key auth on all protected routes
- OpenAPI spec available at /openapi.json, Swagger at /docs
- Docker image built and container running as client-hub-api

.. _client-hub-changelog-2026-04-05f:

2026-04-05 — TDD Strategy and SDK Generation Plan
======================================================================

- Added TDD testing strategy to API design: every endpoint must have
  a test written before or alongside it, hitting real DB (not mocks)
- Added SDK generation section: auto-generate Python, PHP, TypeScript
  SDKs from OpenAPI spec via ``scripts/generate-sdks.sh``
- Expanded project structure with full test file listing (one per
  router module)
- Updated TODO.rst with Phase 6 (SDK Generation), Phase 7 (CI/CD
  Pipeline), and expanded Phase 5 with per-endpoint test requirements
- Added Future section to TODO.rst for planned integrations

.. _client-hub-changelog-2026-04-05e:

2026-04-05 — Data-First Reframing and Schema Enhancements
======================================================================

- Reframed project as **data-first customer intelligence microservice**
- Added ``marketing_opt_out_sms/email/phone`` boolean flags to contacts
- Added ``contact_preferences`` table (flexible key-value per contact)
- Created ``v_contact_summary`` view (holistic intelligence: lifetime
  value, order stats, communications, opt-outs, tags, sources)
- Created ``v_contact_last_order`` view (last order details per contact)
- Updated API design with preference, marketing, and intelligence
  endpoints
- Updated all docs (CLAUDE.md, data-model.rst, api-design.rst) to
  reflect data-first approach and new schema objects
- Schema now: 31 tables + 2 views (was 30 tables)

.. _client-hub-changelog-2026-04-05d:

2026-04-05 — Phase 3 Complete: Test Data and Validation
======================================================================

- Inserted realistic test data: 5 contacts (2 clients, 1 prospect,
  1 lead, 1 vendor), 2 organizations, 4 orders with line items,
  3 invoices, 3 payments, 7 communications, 3 notes
- Ran 11 validation queries — all passed with zero issues:
  FK integrity, orphan checks, CTI phone lookup, Chatwoot email
  lookup, prospect→client conversion, order→invoice→payment chain,
  junction tables, channel prefs, data provenance, status audit trail
- Created ``migrations/012_seed_test_data.sql`` for reproducibility

.. _client-hub-changelog-2026-04-05c:

2026-04-05 — Phase 1 Complete: Data Model Design
======================================================================

- Created comprehensive ``docs/data-model.rst`` (30 tables total)
- 17 entity tables: business_settings, contacts, organizations,
  contact_phones, contact_emails, contact_addresses, org_phones,
  org_emails, org_addresses, contact_channel_prefs, contact_notes,
  orders, order_items, order_status_history, invoices, payments,
  communications
- 2 junction tables: contact_tag_map, contact_marketing_sources
- 11 lookup tables: contact_types, phone_types, email_types,
  address_types, channel_types, marketing_sources, order_statuses,
  order_item_types, invoice_statuses, payment_methods, tags
- Full 3NF normalization analysis with documented denormalization
  decisions
- Corrected tenant model: single-tenant (one DB per business), not
  multi-tenant
- Development database: ``clienthub`` on shared MariaDB
  (originally ``dev_schema``; renamed during the
  standardization sweep on 2026-04-24)

.. _client-hub-changelog-2026-04-05b:

2026-04-05 — Align with Shared MariaDB Infrastructure
======================================================================

- Removed standalone MariaDB container from ``docker-compose.yml``
- Switched to shared MariaDB 12.2.2 at ``~/docker/mariadb/`` on port
  3306 via ``my-main-net``
- Updated all docs to reference shared MariaDB and MySQL MCP Server
  (DBHub) for schema design workflow
- ``docker-compose.yml`` now a placeholder for Phase 2 API container
- Updated ``.env.example`` with simplified DB credentials

.. _client-hub-changelog-2026-04-05:

2026-04-05 — Initial Project Scaffolding
======================================================================

- Created project scaffolding with all standard files (CLAUDE.md,
  README.rst, CHANGELOG.rst, TODO.rst, docs/, .gitignore)
- Added ``docker-compose.yml`` (initially with standalone MariaDB)
- Added ``.env.example`` with database credential templates
- Created ``docs/architecture.rst`` with detailed architecture docs
- Created ``init/`` directory for SQL initialization scripts
- Project status: Phase 1 — Data model design
