.. _client-hub-deployment:

######################################################################
Client Hub — Deployment Guide
######################################################################

.. _client-hub-deploy-quickstart:

**********************************************************************
Quick Start (One-Line Install)
**********************************************************************

On a fresh Ubuntu 22.04/24.04 LTS or Debian 12+ VPS:

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh | sudo bash

Non-interactive (for automation):

.. code-block:: bash

   curl -fsSL https://raw.githubusercontent.com/stancel/client-hub/master/scripts/install.sh \
     | sudo bash -s -- \
     --mode bundled \
     --domain client-hub.example.com \
     --admin-email admin@example.com \
     --first-source-code my_website \
     --first-source-name "My Website" \
     --sdks typescript \
     --non-interactive

.. _client-hub-deploy-sizing:

**********************************************************************
VPS Sizing
**********************************************************************

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Tier
     - Specs
     - Cost (DO)
     - Notes
   * - Minimum
     - 1 vCPU / 2 GB RAM / 25 GB SSD
     - ~$12/mo
     - Sufficient for single-site
   * - Comfortable
     - 2 vCPU / 4 GB RAM / 50 GB SSD
     - ~$24/mo
     - Multiple integrations
   * - External DB
     - 1 vCPU / 1 GB RAM / 25 GB SSD
     - ~$6/mo
     - API + Caddy only

.. _client-hub-deploy-what-installer-does:

**********************************************************************
What the Installer Does
**********************************************************************

1. Detects OS (Ubuntu/Debian only, refuses others)
2. Installs Docker + docker-compose plugin + system packages
3. Creates ``clienthub`` system user
4. Clones the repo to ``/opt/client-hub``
5. Auto-generates all secrets (``openssl rand -hex 32``)
6. Writes ``/opt/client-hub/.env`` (mode 0600)
7. Starts MariaDB + API + Caddy via docker-compose
8. Runs all migrations idempotently
9. Creates the first source and API key
10. Configures UFW firewall
11. Sets up nightly backup cron job
12. Runs smoke tests
13. Prints credentials and next steps

.. _client-hub-deploy-backups:

**********************************************************************
Backups
**********************************************************************

Nightly automated backups via ``/etc/cron.daily/client-hub-backup``:

- Dumps MariaDB to ``/opt/client-hub/backups/``
- Compressed with gzip
- 7-day retention (configurable via ``BACKUP_RETENTION`` env var)
- Logged to ``/var/log/client-hub/backup.log``

Manual backup:

.. code-block:: bash

   /opt/client-hub/scripts/backup.sh

.. _client-hub-deploy-opsinsights:

**********************************************************************
OpsInsights Access
**********************************************************************

The bundled compose does NOT expose MariaDB to the host by default.
For OpsInsights SSH tunnel access, create an override:

.. code-block:: yaml

   # /opt/client-hub/docker-compose.override.yml
   services:
     mariadb:
       ports:
         - "127.0.0.1:3306:3306"

Then from the OpsInsights server:

.. code-block:: bash

   ssh -N -L 13306:127.0.0.1:3306 root@your-clienthub-domain.com
   mariadb -h 127.0.0.1 -P 13306 -u clienthub -p clienthub

.. _client-hub-deploy-uninstall:

**********************************************************************
Uninstall
**********************************************************************

.. code-block:: bash

   # Preserves backups
   sudo /opt/client-hub/scripts/uninstall.sh

   # Full purge including backups
   sudo /opt/client-hub/scripts/uninstall.sh --purge
