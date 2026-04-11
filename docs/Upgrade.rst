.. _client-hub-upgrade:

######################################################################
Client Hub — Upgrade Guide
######################################################################

.. _client-hub-upgrade-process:

**********************************************************************
Upgrade Process
**********************************************************************

1. **Back up** the database before any upgrade:

   .. code-block:: bash

      /opt/client-hub/scripts/backup.sh

2. **Pull latest code:**

   .. code-block:: bash

      cd /opt/client-hub
      git pull --ff-only

3. **Run migrations** (idempotent — safe to re-run):

   .. code-block:: bash

      /opt/client-hub/scripts/bootstrap-migrations.sh \
        --host 127.0.0.1 --user root \
        --password "$(grep MARIADB_ROOT_PASSWORD .env | cut -d= -f2)" \
        --database clienthub

4. **Rebuild and restart** the API:

   .. code-block:: bash

      COMPOSE_FILE=docker-compose.bundled.yml  # or bundled-nodomain
      docker compose -f $COMPOSE_FILE build --quiet
      docker compose -f $COMPOSE_FILE up -d

5. **Smoke test:**

   .. code-block:: bash

      /opt/client-hub/scripts/smoke-test.sh \
        --url http://127.0.0.1:8800 \
        --api-key "$(grep CLIENTHUB_ROOT_API_KEY .env | cut -d= -f2)"

6. **Regenerate SDKs** (if API changed):

   .. code-block:: bash

      /opt/client-hub/scripts/generate-sdks.sh

.. _client-hub-upgrade-key-rotation:

**********************************************************************
API Key Rotation
**********************************************************************

To rotate a source's API key:

1. Create a new key via the admin API:

   .. code-block:: bash

      curl -X POST -H "X-API-Key: ROOT_KEY" \
        -H "Content-Type: application/json" \
        -d '{"name": "Rotated key 2026-04"}' \
        https://your-domain/api/v1/admin/sources/SOURCE_UUID/api-keys

2. Update the integration to use the new key
3. Verify the integration works with the new key
4. Revoke the old key:

   .. code-block:: bash

      curl -X DELETE -H "X-API-Key: ROOT_KEY" \
        https://your-domain/api/v1/admin/api-keys/OLD_KEY_UUID

To rotate the **root key**: update ``CLIENTHUB_ROOT_API_KEY`` in
``/opt/client-hub/.env`` and restart the API container.

.. _client-hub-upgrade-rollback:

**********************************************************************
Rollback
**********************************************************************

If an upgrade fails:

1. Stop containers
2. Restore from backup:

   .. code-block:: bash

      docker compose -f $COMPOSE_FILE exec -T mariadb \
        mariadb -u root -p"$MARIADB_ROOT_PASSWORD" clienthub \
        < /opt/client-hub/backups/clienthub-TIMESTAMP.sql.gz

3. Check out the previous version: ``git checkout PREVIOUS_COMMIT``
4. Rebuild and restart

**Warning:** Database migrations may be one-way. Always back up
before upgrading.
