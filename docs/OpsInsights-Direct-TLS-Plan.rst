======================================================================
OpsInsights → Client Hub: Direct MySQL over TLS + IP Allowlist
======================================================================

:Status: IMPLEMENTED for Clever Orchid on 2026-04-18. **Two
         deviations from plan in production** — global
         ``require_secure_transport`` not set (would break internal
         API), and ``REQUIRE SSL`` on the user was dropped at
         runtime because OpsInsights cannot negotiate TLS (known
         bug in their hardcoded ADOdb PDO driver). See "As
         implemented" section for full details.
:Use case: Persistent, low-latency, read-only access from the
           OpsInsights SaaS backend to each customer Client Hub's
           MariaDB. Feeds live dashboards.
:Alternative: See ``OpsInsights-SSH-Tunnel-Plan.rst`` for the
              read/write enrichment path (autossh-based tunnel).

.. _why-this-pattern:

Why this pattern
======================================================================

Matches the existing published OpsInsights client-onboarding docs at
``https://connect.opsinsights.com/instructions/index.html`` — the
"open firewall access, forward to SQL Server local IP and port, and
whitelist IP addresses" section.

The OpsInsights SaaS has two stable egress IPs:

- ``52.72.248.4`` — AWS NAT Gateway, all application traffic
- ``52.207.33.249`` — OpenVPN server, manual/operator traffic

OpsInsights enforces SSL on the client side, so MariaDB must be
reachable over TLS (self-signed acceptable; publicly-trusted cert
preferred and used here via Caddy's existing Let's Encrypt).

This pattern scales linearly as new Client Hub customers are
onboarded — each host gets its own firewall rules + TLS cert + RO
user; the OpsInsights backend stores per-client connection strings
and queries each DB natively over MySQL protocol.

.. _architecture:

Architecture
======================================================================

::

    OpsInsights SaaS backend
            │
            │  MySQL/TCP on port 3306, TLS required, client SSL
            ▼
    Internet (host firewall allows only 52.72.248.4 + 52.207.33.249)
            │
            ▼
    165.245.130.39:3306  (client-hub.cleverorchid.com)
            │
            │  Docker port publish → container 3306
            ▼
    clienthub-mariadb  (MariaDB 12.2, TLS cert mounted from Caddy)

Firewall enforcement lives in the iptables ``DOCKER-USER`` chain
because Docker's port-publishing bypasses UFW. Rules persist
across reboots via ``iptables-persistent``.

.. _host-side-setup:

Client Hub host setup (165.245.130.39)
======================================================================

1. **Add ``client-hub.cleverorchid.com`` to Caddyfile** so Caddy
   acquires a Let's Encrypt cert for that hostname (the same DNS
   A-record already resolves here). The new block proxies to the
   same FastAPI as the existing ``onlinesalessystems.com``
   hostname — it's just there to trigger ACME issuance:

   .. code-block:: caddy

       client-hub.cleverorchid.com {
           encode gzip
           reverse_proxy client-hub-api:8800
           log {
               output file /var/log/caddy/access.log
               format json
           }
       }

   Reload Caddy (``docker exec clienthub-caddy caddy reload
   --config /etc/caddy/Caddyfile`` or restart the container).
   Wait ~30 seconds for ACME HTTP-01 to complete.

2. **Locate the acquired cert + key**. Caddy stores per-domain
   materials under its data volume at::

       /data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/client-hub.cleverorchid.com/

   The files are ``client-hub.cleverorchid.com.crt`` and
   ``client-hub.cleverorchid.com.key``.

3. **Create ``/opt/client-hub/docker-compose.override.yml``**:

   .. code-block:: yaml

       services:
         clienthub-mariadb:
           ports:
             - "3306:3306"
           volumes:
             - caddy-data:/caddy-certs:ro
           command:
             - --ssl-cert=/caddy-certs/certificates/acme-v02.api.letsencrypt.org-directory/client-hub.cleverorchid.com/client-hub.cleverorchid.com.crt
             - --ssl-key=/caddy-certs/certificates/acme-v02.api.letsencrypt.org-directory/client-hub.cleverorchid.com/client-hub.cleverorchid.com.key
             - --require-secure-transport=ON

       volumes:
         caddy-data:
           external: true
           name: client-hub_caddy_data    # replace with actual Caddy volume name

   ``--require-secure-transport=ON`` forces all connections to use
   TLS, not just the ``opsinsights_ro`` user — defense in depth.

   Apply::

       cd /opt/client-hub
       docker compose up -d

4. **Create a read-only MariaDB user**:

   .. code-block:: sql

       CREATE USER 'opsinsights_ro'@'%'
         IDENTIFIED BY '<STRONG_RANDOM_32>'
         REQUIRE SSL;

       GRANT SELECT ON clienthub.* TO 'opsinsights_ro'@'%';

       FLUSH PRIVILEGES;

   ``REQUIRE SSL`` means MariaDB will reject any non-TLS
   connection for this user, even if global
   ``require-secure-transport`` is off.

5. **Install iptables-persistent + add DOCKER-USER rules**. Docker
   publishes ports by manipulating iptables directly, bypassing
   UFW. The correct place to filter Docker-published ports is the
   ``DOCKER-USER`` chain::

       apt-get update
       DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent

   Add rules (insert at top, order: allows first, then drop)::

       iptables -I DOCKER-USER -p tcp --dport 3306 -j DROP
       iptables -I DOCKER-USER -p tcp --dport 3306 -s 52.207.33.249 -j ACCEPT
       iptables -I DOCKER-USER -p tcp --dport 3306 -s 52.72.248.4 -j ACCEPT

       # IPv6 equivalent (deny by default since allowlist is IPv4-only):
       ip6tables -I DOCKER-USER -p tcp --dport 3306 -j DROP

   Save::

       netfilter-persistent save

   Verify::

       iptables -L DOCKER-USER -n --line-numbers
       # expect lines 1-2 = ACCEPT from exit IPs, line 3 = DROP, line 4 = RETURN

.. _connection-string:

Connection string
======================================================================

Plug this into OpsInsights::

    Host:     client-hub.cleverorchid.com
    Port:     3306
    Database: clienthub
    User:     opsinsights_ro
    Password: <generated at implementation time — see handoff>
    SSL:      required (server has publicly-trusted Let's Encrypt cert)

URI form::

    mysql://opsinsights_ro:<PASSWORD>@client-hub.cleverorchid.com:3306/clienthub?ssl-mode=REQUIRED

Python SQLAlchemy (PyMySQL driver)::

    mysql+pymysql://opsinsights_ro:<PASSWORD>@client-hub.cleverorchid.com:3306/clienthub?ssl=true&ssl_verify_cert=true&charset=utf8mb4

.. _verification:

Verification
======================================================================

1. **Port 3306 listens publicly**::

       ssh root@165.245.130.39 'ss -tlnp | grep :3306'
       # expect: 0.0.0.0:3306 LISTEN docker-proxy

2. **TLS handshake works** (from inside the container, bypassing
   firewall)::

       docker exec clienthub-mariadb mariadb \
         -h 127.0.0.1 -u opsinsights_ro -p \
         --ssl --ssl-verify-server-cert clienthub \
         -e "STATUS;"
       # expect: "SSL: Cipher in use is ..." (not "Not in use")

3. **Allowlist works** — from a non-whitelisted host (e.g., brad's
   workstation)::

       nc -zv client-hub.cleverorchid.com 3306
       # expect: connection refused / timeout (DROP in DOCKER-USER)

4. **From OpsInsights SaaS** (52.72.248.4 egress): Brad will test
   the dashboard hookup with the handed-off credentials.

5. **Read-only verified**::

       # Run from OpsInsights side once connected
       INSERT INTO sources (code,name) VALUES ('x','y');
       # expect: ERROR 1142 (42000): INSERT command denied

.. _scaling-to-more-clients:

Scaling to more Client Hub instances
======================================================================

Each new Client Hub deploys get:

1. DNS record for ``client-hub.<customer-domain>``
2. Caddyfile entry for that hostname (auto-issues LE cert)
3. ``docker-compose.override.yml`` binding MariaDB on 3306
4. ``opsinsights_ro`` user (reuse username; unique password per
   instance)
5. DOCKER-USER iptables rules for 52.72.248.4 and 52.207.33.249
6. Hand connection string to OpsInsights

Recommend adding a ``--opsinsights-tls`` flag to
``scripts/install.sh`` that bundles these steps into the installer
so onboarding a new customer is one command.

.. _security-notes:

Security notes
======================================================================

- **IP allowlist is the primary control**; TLS + REQUIRE SSL is
  secondary defense. Even if OpsInsights creds leaked, only the
  two allowlisted source IPs can open a socket on 3306.
- **Read-only user** per customer scopes the damage-if-compromised
  to read-level SELECT on that customer's Client Hub schema.
- **Publicly-trusted Let's Encrypt cert** (via Caddy) means
  OpsInsights can do strict hostname + chain verification without
  configuring any CA trust.
- Cert renewal is automatic via Caddy (60-day renewal). MariaDB
  holds file handles to the cert; need to ``docker compose restart
  clienthub-mariadb`` after Caddy renewal to re-read the cert.
  Consider adding a monthly cron that restarts MariaDB on the 15th
  of each month (well outside the 30-day renewal buffer).
- **No GRANT OPTION** on ``opsinsights_ro`` — it cannot create
  other users.
- **MariaDB root password** remains in ``/opt/client-hub/.env``,
  file mode ``0600``, owned by ``clienthub:clienthub``.

.. _as-implemented:

As implemented — Clever Orchid, 2026-04-18
======================================================================

Actual changes made on ``root@165.245.130.39`` (Clever Orchid
Client Hub VPS):

**Caddyfile** (``/opt/client-hub/Caddyfile``) — backup at
``Caddyfile.bak-pre-tls``. Added a second site block for
``client-hub.cleverorchid.com`` so Caddy acquires a Let's Encrypt
cert for that name. The existing
``client-hub-clever-orchid.onlinesalessystems.com`` block is
unchanged.

**Cert staging** — copied Caddy-issued cert files from::

    /opt/client-hub/data/caddy/caddy/certificates/acme-v02.api.letsencrypt.org-directory/client-hub.cleverorchid.com/

to::

    /opt/client-hub/data/mariadb-tls/server.crt (0640, uid/gid 999:999)
    /opt/client-hub/data/mariadb-tls/server.key (0600, uid/gid 999:999)

UID/GID 999 = ``mysql`` user inside the MariaDB container.

**docker-compose.bundled.yml** (backup at
``docker-compose.bundled.yml.bak-pre-tls``) — added to the
``mariadb`` service:

- ``ports: - "3306:3306"`` (publishes on all host interfaces)
- Volume mount ``./data/mariadb-tls:/etc/mysql-tls:ro``
- Command args ``--ssl-cert=/etc/mysql-tls/server.crt`` and
  ``--ssl-key=/etc/mysql-tls/server.key``

**Deviation from plan: no global** ``--require-secure-transport=ON``.
Applying it globally would have rejected the internal API-
container → MariaDB connection (the FastAPI container connects
over plain TCP via the Docker ``clienthub`` network, not TLS).
REQUIRE SSL is set per-user on ``opsinsights_ro`` — that achieves
the same defense-in-depth for the OpsInsights connection without
breaking the production conversion-tracking integration. Verified
working: non-TLS connection as ``opsinsights_ro`` returns
``ERROR 1045 (28000): Access denied``.

**iptables DOCKER-USER chain** (persisted via
``iptables-persistent``, saved to
``/etc/iptables/rules.v4``)::

    1  ACCEPT  tcp  -- 52.72.248.4     0.0.0.0/0  tcp dpt:3306
    2  ACCEPT  tcp  -- 52.207.33.249   0.0.0.0/0  tcp dpt:3306
    3  DROP    tcp  -- 0.0.0.0/0       0.0.0.0/0  tcp dpt:3306

IPv6 DOCKER-USER has a blanket DROP on tcp/3306 (the allowlist IPs
are IPv4-only).

**MariaDB user** created::

    CREATE USER 'opsinsights_ro'@'%' IDENTIFIED BY '<32-char random>' REQUIRE SSL;
    GRANT SELECT ON clienthub.* TO 'opsinsights_ro'@'%';
    FLUSH PRIVILEGES;

Password is stored on the host at
``/opt/client-hub/data/opsinsights_credentials.txt`` (mode 0600,
root-owned) for retrieval.

**Verification results (2026-04-18):**

+------------------------------------------+----------------------+
| Test                                     | Result               |
+==========================================+======================+
| TLS login from inside container          | ``Cipher in use is   |
|                                          | TLS_AES_256_GCM_SHA  |
|                                          | 384, cert is OK``    |
+------------------------------------------+----------------------+
| Non-TLS connection as opsinsights_ro     | ``ERROR 1045 Access  |
|                                          | denied``             |
+------------------------------------------+----------------------+
| Read-only grants                         | SELECT works,        |
|                                          | INSERT would fail    |
|                                          | (not tested — user   |
|                                          | has no INSERT grant) |
+------------------------------------------+----------------------+
| TCP connect from non-whitelisted IP      | Timeout (DROP in     |
| (Cybertron)                              | DOCKER-USER)         |
+------------------------------------------+----------------------+
| MySQL connect from non-whitelisted IP    | ``ERROR 2002 Can't   |
| (Cybertron)                              | connect``            |
+------------------------------------------+----------------------+
| FastAPI container still posting events   | ``clienthub-api Up   |
|                                          | 6 days``, no errors  |
|                                          | in logs              |
+------------------------------------------+----------------------+
| New HTTPS endpoint                       | ``client-hub.clever  |
|                                          | orchid.com`` serves  |
|                                          | with LE cert         |
+------------------------------------------+----------------------+

**Operational note — cert renewal:** Caddy auto-renews every ~60
days. The cert files bind-mounted into MariaDB point at a **copy**
in ``./data/mariadb-tls/``, so the copy must be refreshed + MariaDB
restarted after renewal. TODO: add a ``scripts/refresh-mariadb-
tls.sh`` + systemd timer (or Caddy ``exec`` directive on the
renewal hook) to automate this. Until that's in place, schedule a
monthly manual refresh or set a reminder for mid-June 2026.

.. _require-ssl-dropped-interim:

Deviation — REQUIRE SSL dropped (interim, 2026-04-18)
----------------------------------------------------------------------

Initial deployment created the user with ``REQUIRE SSL``. During
end-to-end verification, OpsInsights could not negotiate TLS on
its MySQL connection and was rejected with ``SQLSTATE[HY000]
[1045]``. Investigation into
``~/Sites/ops-insights/_protected/common/impl/reportEngine/ADOdb/drivers/adodb-pdo.inc.php``
line 149 found that OpsInsights' hardcoded ADOdb PDO driver calls
``new PDO($dsn, $user, $pass)`` with only 3 arguments — no options
array. ``PDO::MYSQL_ATTR_SSL_*`` constants **must** be passed as
the 4th argument to the constructor; setting them via
``setAttribute()`` after construction is silently ignored by
PDO_MySQL. So no amount of OpsInsights-side configuration can
enable SSL with the current code.

Secondary finding: ``ConnectorImpl::connect_driver_pdo_mysql()``
uses ``getUseEncryptedConnection()`` to toggle ``PConnect`` vs
``Connect`` (persistence, not encryption). The flag name lies;
meanwhile ``use_persistent_connection`` is a separate column on
``ClientDatabases`` that the MySQL path ignores entirely. Schema
and UI are correctly designed; only the connect method is wired
to the wrong column.

**Interim decision:** Drop ``REQUIRE SSL`` from the
``opsinsights_ro`` user on the Clever Orchid Client Hub host
(``ALTER USER 'opsinsights_ro'@'%' REQUIRE NONE``). Security now
rests on:

- iptables ``DOCKER-USER`` allowlist (only ``52.72.248.4`` and
  ``52.207.33.249`` can reach port 3306)
- MariaDB auth (32-char random password)
- ``SELECT``-only grants on ``clienthub``

Plaintext traffic flows between AWS NAT Gateway and DigitalOcean —
MITM on Tier-1 backbone is very unlikely but not zero.

**Revisit during the OpsInsights modernization pass** (Greptile +
Claude Code). At that point: apply the two patches documented in
the memory note ``project_opsinsights_adodb_pdo_ssl_bug.md`` and
then re-add ``REQUIRE SSL`` to restore full defense-in-depth. Also
adjust the script default at that time.

For **new Client Hub deployments** before the OpsInsights fix is
in, use ``scripts/setup-opsinsights-tls.sh`` without
``--require-ssl`` (the default). After the OpsInsights fix ships,
update the script default and pass ``--require-ssl`` at deploy
time.
