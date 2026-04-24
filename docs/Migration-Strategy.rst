.. _client-hub-migration-strategy:

######################################################################
Client Hub — Schema Migration & Release Strategy
######################################################################

.. _client-hub-ms-overview:

**********************************************************************
Overview
**********************************************************************

This document is the durable playbook for changing the Client Hub
data model and shipping the resulting API / SDK changes. It codifies
the pattern used for the multi-org refactor (migrations 019–022) so
future schema refactors follow the same shape.

Client Hub is a **self-contained microservice**: one code repository,
one database, a bounded set of consumers (a REST API, three
auto-generated SDKs, and optional direct-SQL integrations). Because
the surface is self-contained we can bundle schema, code, tests,
SDKs, and docs into a single release rather than orchestrating
multi-service rollouts. This document explains how to do that
cleanly and reversibly.

.. _client-hub-ms-principles:

**********************************************************************
Core Principles
**********************************************************************

1. **Maintain 3NF.** The schema is the product. When a design
   decision pits a denormalized cached-pointer shortcut against a
   junction-table or lookup-table refactor, always pick the
   normalized path — even when the migration surface is larger. The
   canonical example is migrations 019–021, which replaced
   ``contacts.organization_id`` with ``contact_org_affiliations``.

2. **Idempotent SQL.** Every migration must be safe to re-run on
   any target state. Use ``CREATE TABLE IF NOT EXISTS``,
   ``INSERT ... ON DUPLICATE KEY UPDATE`` (or ``INSERT IGNORE``),
   ``ALTER TABLE ... ADD COLUMN IF NOT EXISTS``,
   ``ALTER TABLE ... ADD KEY IF NOT EXISTS``, and
   INFORMATION_SCHEMA-guarded dynamic SQL for ``ADD CONSTRAINT``
   and ``DROP COLUMN``. Never rely solely on the
   ``_schema_migrations`` tracker — treat it as one line of defense,
   SQL idempotency as the other.

3. **TDD — tests lead.** Write failing tests for the new API
   surface *before* writing migrations or code. This forces clarity
   on the desired consumer-facing shape and yields green CI as a
   deterministic signal that the refactor landed correctly.

4. **Bundle schema + code + SDKs + docs in one PR.** No dual-write
   eras, no temporary shims. API consumers update via regenerated
   SDKs, or direct-SQL consumers update their queries. This is
   acceptable because the microservice is small-consumer.

5. **Commit in logical chunks inside the PR.** Each commit should
   be individually reviewable and ideally revertible. Split
   migrations from code from SDK regen from docs.

6. **Backup before every production migration.** The
   ``./scripts/backup.sh`` helper is the canonical rollback path.
   Reverse SQL in migration comments is for reference only.

.. _client-hub-ms-phases:

**********************************************************************
Release Phases
**********************************************************************

A schema change moves through five phases. Each phase has a clear
exit gate.

.. _client-hub-ms-phase-design:

Phase 1 — Design (docs-first)
======================================================================

Before writing any SQL or code:

1. Update ``docs/data-model.rst``:

   - Add / modify table-definition sections (columns, types,
     nullability, FKs, indexes)
   - Update ``v_contact_summary`` or other view definitions if
     affected
   - Add the Junction Tables Summary entry if a new junction
     is introduced
   - Update the Complete Table List at the end
   - Explain the 3NF rationale in a ``Normalization`` block

2. Update ``docs/api-design.rst`` with any new endpoints,
   payload field changes, or breaking-change notices.

3. Update ``docs/Cross-Project-Integration.rst`` if the payload
   contract changes.

4. Lint: ``rstcheck --report-level warning docs/*.rst``.

5. **Gate:** commit the design documentation and get sign-off
   before writing migrations or code. This keeps review focused
   on the *shape* of the change before the mechanical work lands.

.. _client-hub-ms-phase-migrations:

Phase 2 — Write migrations (idempotent, numbered, rollback-noted)
======================================================================

1. Pick the next numbered prefix (``ls migrations/ | tail``).
   Use one file per logically distinct DDL step so reviewers and
   ``bootstrap-migrations.sh`` can reason about each change
   separately.

2. Idempotency patterns:

   - **Create tables**: ``CREATE TABLE IF NOT EXISTS``
   - **Seed rows**: ``INSERT ... ON DUPLICATE KEY UPDATE`` (to
     refresh labels/sort orders), or ``INSERT IGNORE`` for pure
     inserts.
   - **Add columns**: ``ALTER TABLE ... ADD COLUMN IF NOT EXISTS``
   - **Add indexes**: ``ALTER TABLE ... ADD KEY IF NOT EXISTS``
   - **Add constraints (FK)**: INFORMATION_SCHEMA guard around
     dynamic SQL:

     .. code-block:: sql

        SET @fk_exists := (
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'my_table'
              AND CONSTRAINT_NAME = 'fk_my_constraint'
        );
        SET @sql := IF(@fk_exists = 0,
            'ALTER TABLE my_table ADD CONSTRAINT fk_my_constraint FOREIGN KEY ...',
            'SELECT 1');
        PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

   - **Drop columns / FKs / indexes**: same INFORMATION_SCHEMA guard
     pattern, checking for existence *before* dropping.
   - **Rewrite views**: ``DROP VIEW IF EXISTS`` + ``CREATE VIEW``
     (not ``CREATE OR REPLACE`` if column list changes — a fresh
     drop-and-create avoids column-mapping surprises).

3. Backfill data *within* the migration that introduces the new
   shape, guarded by ``NOT EXISTS`` so re-runs are safe. If the
   backfill depends on a column that a later migration will drop,
   guard the backfill with an INFORMATION_SCHEMA column-exists
   check so it no-ops cleanly once the column is gone.

4. Enforce new DB-level invariants using virtual generated
   columns + composite UNIQUE indexes where the invariant is
   "at most one row per group with flag=TRUE." See migrations
   019 and 022 for the canonical pattern:

   .. code-block:: sql

      is_primary_key TINYINT UNSIGNED
          GENERATED ALWAYS AS (IF(is_primary, 1, NULL)) VIRTUAL,
      UNIQUE KEY ux_name (group_col, is_primary_key)

   This is preferred over ``BEFORE INSERT/UPDATE`` triggers
   (harder to debug, slower, and don't survive mariadb-dump
   cleanly). Prefer VIRTUAL over STORED — it is metadata-only and
   adds no row storage.

5. Document the **reverse SQL** as a trailing comment block in
   any migration that is not trivially reversible. Treat it as
   reference only; the real rollback path is a backup restore.

6. **Gate:** apply the migrations against the dev database via
   the ``apisix-mysql`` MCP tool (``execute_sql``) and verify with
   ``search_objects``. Re-run them to confirm idempotency. Back
   out with a restored backup if anything is unclear.

.. _client-hub-ms-phase-tdd:

Phase 3 — TDD cycle (tests, models, schemas, routers, green)
======================================================================

1. **Write failing tests first.** New endpoints, changed response
   shapes, and new request fields all get tests before code.
   Tests hit the real database per ``feedback_tdd_and_sdks``.

2. Update SQLAlchemy models (``api/app/models/``) to match the
   new schema. Add new model classes for new tables. Drop
   columns / relationships that went away.

3. Update Pydantic schemas (``api/app/schemas/``). Remove fields
   that were backed by dropped columns. Add fields for new
   capability (e.g., nested affiliation objects, nullable
   ``affiliation_uuid`` on detail rows). **Do not** add
   backwards-compat alias fields — clean breaks only.

4. Update services and routers (``api/app/services/``,
   ``api/app/routers/``). Add a new router file for new endpoint
   groups (e.g., ``affiliations.py``).

5. Run ``pytest -v`` until green. ``ruff check`` clean.

6. **Gate:** CI must be green on the feature branch before
   proceeding to SDK regen.

.. _client-hub-ms-phase-sdks:

Phase 4 — Regenerate SDKs + release artifacts
======================================================================

1. Run ``./scripts/generate-sdks.sh`` — regenerates Python, PHP,
   and TypeScript from the current OpenAPI spec.

2. Commit the regenerated SDKs in a standalone commit
   (``chore(sdk): regenerate ...``). Keeps review diff tractable.

3. Update ``CHANGELOG.rst`` with a dated entry describing the
   release, breaking changes, and any upgrade instructions.

4. Update ``TODO.rst`` — mark completed items, add new phase
   entry if this is a large refactor.

5. Update ``CLAUDE.md`` and ``README.rst`` if counts or headline
   facts (table counts, endpoint counts, test counts) change.

6. Lint: ``rstcheck --report-level warning docs/*.rst
   README.rst CHANGELOG.rst TODO.rst``.

.. _client-hub-ms-phase-deploy:

Phase 5 — Deploy to live VPS instances
======================================================================

Per live installation (currently only Complete Dental Care):

.. code-block:: bash

   # 1. Backup (mandatory)
   cd /opt/client-hub
   ./scripts/backup.sh

   # 2. Pull the bundled release
   git fetch origin master
   git reset --hard origin/master

   # 3. Stop and rebuild
   docker compose down
   docker compose build

   # 4. Run pending migrations (idempotent; tracked in _schema_migrations)
   ./scripts/bootstrap-migrations.sh

   # 5. Start
   docker compose up -d

   # 6. Smoke test
   ./scripts/smoke-test.sh

   # 7. Notify consumer repos to upgrade their regenerated SDK
   #    (e.g. the Dental Care Next.js site's @client-hub/typescript-sdk)

Rollback: restore from the step-1 backup and revert ``client-hub``
to the prior git tag.

.. _client-hub-ms-commit-shape:

**********************************************************************
Commit Shape Inside the Release PR
**********************************************************************

One feature branch off ``master`` (per ``feedback_master_branch``).
One PR. Commits sequenced for incremental review:

1. ``docs: document new <name> design in data-model.rst``
2. ``feat(db): <migration-group-a> (migrations NNN-MMM)``
3. ``feat(db): <migration-group-b> (migrations PPP-QQQ)``
4. ``feat(api): <capability-name> — models, schemas, routers, tests``
5. ``chore(sdk): regenerate Python/PHP/TypeScript SDKs``
6. ``docs: <any remaining docs + CHANGELOG + TODO updates>``

Merge via standard GitHub PR once CI is green.

.. _client-hub-ms-breaking-changes:

**********************************************************************
Handling Breaking Changes
**********************************************************************

Until Client Hub has external API consumers (other teams or
customers integrating directly against the REST API), breaking
changes to ``/api/v1`` are acceptable and preferred over
dual-versioning. Rationale:

- In-house consumers use the auto-generated SDKs, which regenerate
  cleanly from the new OpenAPI spec.
- Direct-SQL consumers (MCP tools, OpsInsights read-only operator
  queries) query views and tables, not the REST API, and their
  update path is "edit the query."
- Maintaining ``/api/v1`` alongside ``/api/v2`` doubles the code
  surface for marginal benefit while we have one live integration.

Once there are multiple external API consumers we don't control,
introduce ``/api/v2`` rather than breaking ``/api/v1``.

Flag every breaking change in ``CHANGELOG.rst`` under a
``**Breaking changes:**`` subsection with:

- Field renames (old name → new name)
- Field removals (with replacement, if any)
- Endpoint-path changes
- Response-shape changes
- The companion repo(s) that need updates

.. _client-hub-ms-invariants:

**********************************************************************
DB-Level Invariant Enforcement
**********************************************************************

"At most one row per group with flag=TRUE" is the most common
invariant in this schema (primary phone, primary email, primary
address, primary affiliation). Enforce at the DB level using the
generated-column + UNIQUE pattern documented above. Service-layer
checks alone are not sufficient because:

- MCP tools (``apisix-mysql.execute_sql``) can write directly.
- Operator scripts and ops runbooks can write directly.
- Future SaaS operator connections (like OpsInsights) may get
  write grants.

Pair DB-enforced "at most one" with service-layer-enforced
"at least one when any rows exist" to get exactly-one semantics.
The service layer owns promotion (when a primary row is deleted,
promote the next candidate to primary) because "which candidate
gets promoted" is application policy, not a DB invariant.

.. _client-hub-ms-checklist:

**********************************************************************
Pre-Merge Checklist
**********************************************************************

Before merging the release PR:

- [ ] Design documented in ``docs/data-model.rst`` and, if API
  changes, in ``docs/api-design.rst``
- [ ] All new migrations idempotent — verified by re-running
  ``bootstrap-migrations.sh`` against a scratch dev database
- [ ] Backfills guarded by ``NOT EXISTS`` or INFORMATION_SCHEMA
  column-exists checks
- [ ] DB-level invariants enforced (generated-column UNIQUE
  indexes, FKs with appropriate ``ON DELETE`` action)
- [ ] Failing tests written first; all tests green
- [ ] ``ruff check app/ tests/`` clean
- [ ] ``rstcheck --report-level warning`` clean on all edited RST
- [ ] SDKs regenerated
- [ ] ``CHANGELOG.rst`` entry with breaking-change callout
- [ ] ``TODO.rst`` updated
- [ ] ``CLAUDE.md`` / ``README.rst`` updated if counts change
- [ ] Deploy steps rehearsed on a local clone before live VPS

.. _client-hub-ms-references:

**********************************************************************
References
**********************************************************************

- ``scripts/bootstrap-migrations.sh`` — the migration runner
- ``migrations/018_schema_migrations_tracking.sql`` — the
  ``_schema_migrations`` tracking table definition
- ``migrations/019_contact_org_affiliations.sql`` through
  ``022_primary_uniqueness_details.sql`` — canonical examples
  of the full pattern described here
- ``docs/data-model.rst`` — authoritative schema documentation
- ``docs/Deployment.rst`` — production deployment guide
