.. _client-hub-ci-cd:

######################################################################
Client Hub — CI/CD Pipeline
######################################################################

.. _client-hub-ci-cd-overview:

**********************************************************************
Overview
**********************************************************************

Client Hub uses GitHub Actions for continuous integration. The
pipeline runs on every push to ``master`` and on pull requests
targeting ``master``.

.. _client-hub-ci-cd-stages:

**********************************************************************
Pipeline Stages
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Stage
     - Trigger
     - Description
   * - **Lint**
     - All pushes and PRs
     - Python linting with ruff, RST linting with rstcheck
   * - **Test**
     - After lint passes
     - Runs pytest against a MariaDB 12 service container.
       Executes all migrations, seeds data, runs full test suite
       with coverage reporting.
   * - **Build**
     - After test passes
     - Builds the Docker image and verifies it.
   * - **Generate SDKs**
     - Master branch only
     - Starts the API, fetches OpenAPI spec, regenerates
       Python/PHP/TypeScript SDKs, uploads as artifact.

.. _client-hub-ci-cd-test-db:

**********************************************************************
Test Database
**********************************************************************

The CI pipeline provisions a fresh MariaDB 12 service container for
each test run. Migrations are applied in order, then lookup data
and test data are seeded. This matches the local development flow
exactly.

Environment variables for CI tests:

- ``DB_HOST=127.0.0.1``
- ``DB_PORT=3306``
- ``DB_NAME=test_schema``
- ``DB_USER=root``
- ``DB_PASSWORD=test_root_password``
- ``API_KEY=test-api-key``

.. _client-hub-ci-cd-local:

**********************************************************************
Running Locally
**********************************************************************

.. code-block:: bash

   # Lint
   cd ~/docker/client-hub/api
   ruff check app/ tests/
   rstcheck --report-level warning ../docs/*.rst ../CHANGELOG.rst

   # Test
   .venv/bin/python -m pytest tests/ -v --cov=app

   # Build
   docker compose build

   # Generate SDKs
   ../scripts/generate-sdks.sh
