======================================================================
OpsInsights → Client Hub: SSH Tunnel Integration Plan
======================================================================

:Status: Reference plan — not yet implemented
:Created: 2026-04-18
:Use case: Read/write access, interactive queries, data enrichment
           workflows (CTI ingest, InvoiceNinja joins, bulk merges).
           Preferred pattern for non-SaaS-dashboard access paths.
:Alternative: See ``OpsInsights-Direct-TLS-Plan.rst`` for the
              read-only SaaS-dashboard integration that was
              implemented first for Clever Orchid on 2026-04-18.

.. _context:

Context
======================================================================

This document captures the SSH-tunnel connection pattern for
OpsInsights → Client Hub MariaDB. It is preserved for later
implementation when Brad needs to read, write, update, or delete
data in a Client Hub instance — e.g., enriching records with CTI
call data, merging InvoiceNinja contacts, or running bulk data
backfills.

The initial OpsInsights SaaS dashboard hookup uses the
Direct-MySQL-over-TLS + IP-allowlist approach instead (see the
sibling doc). SSH tunneling is the right fit for:

- Interactive analytics / ad-hoc SQL sessions
- Batch enrichment jobs that write back to Client Hub
- Scripts that pull data from multiple sources and merge
- Any connection where read-only is insufficient

.. _architecture:

Architecture
======================================================================

One-hop SSH tunnel, key-auth, restricted to a single port-forward::

    OpsInsights backend host
            │
            │  ssh -L <local>:127.0.0.1:3306   (port 22, ed25519 key)
            ▼
    165.245.130.39  (client-hub.cleverorchid.com)
            │
            │  → Docker's my-main-net
            ▼
    clienthub-mariadb container

Optional 3-hop variant (route through OpsInsights AWS bastion +
NAT Gateway) only matters if Brad wants to lock SSH on the Client
Hub host down to the two documented egress IPs
(``52.72.248.4``, ``52.207.33.249``). SSH key auth is the primary
security control; egress-IP whitelisting is secondary.

.. _host-side-setup:

Client Hub host setup (165.245.130.39)
======================================================================

1. **Bind MariaDB to host localhost only** (not publicly). Create
   ``/opt/client-hub/docker-compose.override.yml``:

   .. code-block:: yaml

       services:
         clienthub-mariadb:
           ports:
             - "127.0.0.1:3306:3306"

   Then::

       cd /opt/client-hub
       docker compose up -d

   MariaDB now listens on the host's ``127.0.0.1:3306`` but is
   unreachable from the public internet. The SSH tunnel will
   connect to this localhost binding.

2. **Create a read-write MariaDB user** (scoped appropriately —
   don't re-use the read-only user from the TLS plan):

   .. code-block:: sql

       CREATE USER 'opsinsights_rw'@'127.0.0.1'
         IDENTIFIED BY '<STRONG_RANDOM_32>';

       -- Minimum grants for dashboard + enrichment work:
       GRANT SELECT, INSERT, UPDATE, DELETE
         ON clienthub.*
         TO 'opsinsights_rw'@'127.0.0.1';

       -- Tighten further by listing specific tables if full
       -- DML grant is too broad. Do NOT grant GRANT OPTION
       -- or admin privileges.

       FLUSH PRIVILEGES;

3. **Create a restricted Linux SSH user**::

       useradd -m -s /bin/false opsinsights
       mkdir -p /home/opsinsights/.ssh
       chmod 700 /home/opsinsights/.ssh
       chown opsinsights:opsinsights /home/opsinsights/.ssh

   Add the OpsInsights backend's ed25519 public key to
   ``/home/opsinsights/.ssh/authorized_keys`` with a restrictive
   prefix::

       command="false",no-pty,no-X11-forwarding,no-agent-forwarding,no-user-rc,permitopen="127.0.0.1:3306" ssh-ed25519 AAAAC3... opsinsights-backend

   ``chmod 600`` the file; ``chown opsinsights:opsinsights``.

   That prefix means: no interactive shell, no agent forwarding,
   no X11, and the only TCP forward permitted is to
   ``127.0.0.1:3306``. Even if the key leaks, the blast radius is
   "SELECT/INSERT/UPDATE/DELETE on clienthub via MariaDB auth".

4. **(Optional hardening) UFW allowlist SSH**::

       ufw allow from 52.72.248.4 to any port 22 proto tcp
       ufw allow from 52.207.33.249 to any port 22 proto tcp
       ufw allow 80,443/tcp
       ufw default deny incoming
       ufw enable

   Only after confirming Brad's current SSH sources are in that
   list. Losing SSH requires DigitalOcean console recovery.

.. _client-side-setup:

OpsInsights side setup
======================================================================

**Option A — autossh systemd unit (recommended for persistent
dashboards):**

Create ``/etc/systemd/system/clienthub-tunnel-clever-orchid.service``:

.. code-block:: ini

    [Unit]
    Description=SSH tunnel to Clever Orchid Client Hub MariaDB
    After=network-online.target
    Wants=network-online.target

    [Service]
    User=opsinsights
    Environment=AUTOSSH_GATETIME=0
    ExecStart=/usr/bin/autossh -M 0 -N \\
        -o ServerAliveInterval=30 \\
        -o ServerAliveCountMax=3 \\
        -o ExitOnForwardFailure=yes \\
        -o StrictHostKeyChecking=accept-new \\
        -i /etc/opsinsights/keys/clienthub_clever_orchid_ed25519 \\
        -L 13306:127.0.0.1:3306 \\
        opsinsights@client-hub.cleverorchid.com
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target

Enable::

    systemctl enable --now clienthub-tunnel-clever-orchid

The OpsInsights backend then connects at ``127.0.0.1:13306``.

**Option B — extend the OpsInsights MCP TunnelManager** with a
``persistent=True`` mode that keeps the ControlMaster socket alive
indefinitely, using the existing
``~/docker/opsinsights-mcp/src/tunnel/ssh.py`` ``create_tunnel()``
primitives. More work but keeps tunnel lifecycle inside the MCP
service.

**Option C — 3-hop via AWS bastion** (only if SSH is allowlisted
to the NAT Gateway egress IPs on the Client Hub host):

.. code-block:: bash

    autossh -M 0 -N \
      -J ec2-user@54.205.237.149:22,ec2-user@10.0.1.236:22 \
      -L 13306:127.0.0.1:3306 \
      opsinsights@client-hub.cleverorchid.com

.. _connection-string:

Connection string
======================================================================

After the tunnel is up locally on the OpsInsights backend::

    mysql://opsinsights_rw:<PASSWORD>@127.0.0.1:13306/clienthub

SQLAlchemy form::

    mysql+pymysql://opsinsights_rw:<PASSWORD>@127.0.0.1:13306/clienthub?charset=utf8mb4

.. _verification:

Verification
======================================================================

1. MariaDB not publicly reachable::

       nc -zv client-hub.cleverorchid.com 3306
       # expect: connection refused or filtered

2. Tunnel opens successfully::

       ssh -v -i <key> -N -L 13306:127.0.0.1:3306 opsinsights@client-hub.cleverorchid.com
       # expect: connection succeeds, no shell, forward open

3. SQL query through tunnel::

       mysql -h 127.0.0.1 -P 13306 -u opsinsights_rw -p clienthub \
         -e "SELECT COUNT(*) FROM contacts;"

4. Shell-restriction verified::

       ssh -i <key> opsinsights@client-hub.cleverorchid.com
       # expect: immediate disconnect (command="false")

5. Other ports blocked::

       ssh -i <key> -L 2222:127.0.0.1:22 opsinsights@client-hub.cleverorchid.com
       # expect: "open failed: administratively prohibited"

.. _scaling-to-more-clients:

Scaling to more Client Hub instances
======================================================================

Each new customer Client Hub gets its own:

- DigitalOcean VPS + hostname
- ``opsinsights`` Linux user + unique SSH key in authorized_keys
- ``opsinsights_rw`` MariaDB user with the same grants
- autossh systemd unit on the OpsInsights backend with a unique
  local port (14306, 15306, ...) and service name

Template this into the Client Hub ``scripts/install.sh`` with a
``--opsinsights-pubkey <ssh-ed25519 ...>`` flag so deployment is
one command.