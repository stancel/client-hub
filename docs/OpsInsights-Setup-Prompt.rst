.. _opsinsights-setup-prompt:

######################################################################
Client Hub — OpsInsights Connection Setup Prompt
######################################################################

:Target audience: Claude Code session opened in ``/opt/client-hub/`` on
                  a customer's Client Hub VPS, OR on the operator's
                  workstation with SSH access to the VPS.
:Created: 2026-04-18
:Proven on: Clever Orchid Embroidery (``client-hub.cleverorchid.com``,
            DigitalOcean VPS ``165.245.130.39``), 2026-04-18
:Estimated scope: 5–10 minutes if everything is wired correctly.
:Related docs: ``OpsInsights-Direct-TLS-Plan.rst`` (the full design
               rationale this prompt automates) and
               ``OpsInsights-SSH-Tunnel-Plan.rst`` (the alternative
               read/write path, for future implementation).


.. contents:: Table of Contents
   :local:
   :depth: 2


**********************************************************************
How to use this document
**********************************************************************

This is a self-contained implementation prompt for connecting a new
Client Hub instance to the OpsInsights SaaS backend. It is meant to be
dropped into any customer's Client Hub install so a Claude Code (or
human operator) session can execute the setup end-to-end without having
to re-derive the architecture.

**The heavy lifting is done by the script**
``scripts/setup-opsinsights-tls.sh`` — this document explains what the
script does, why, and how to verify the result.

**Your job, if you're the implementation session reading this:**

1. Confirm the prerequisites in the next section.
2. Run the script with the right flags for this customer.
3. Run the verification steps.
4. Hand the emitted credentials to the operator so they can plug them
   into OpsInsights.
5. Confirm a live query from OpsInsights before marking the work done.


**********************************************************************
Prerequisites
**********************************************************************

Before running the script, ensure:

- **Client Hub is already installed** at ``/opt/client-hub/`` (or pass
  ``--install-dir``) with the three bundled containers
  (``clienthub-caddy``, ``clienthub-api``, ``clienthub-mariadb``) all
  running. If not, run ``scripts/install.sh`` first.
- **DNS** — the hostname you want MariaDB to be reachable at (e.g.
  ``client-hub.customer.com``) has an A record pointing to this VPS's
  public IP. Let's Encrypt HTTP-01 will fail otherwise.
- **Port 80 is open** on the VPS firewall. Caddy uses it for ACME
  HTTP-01. (Port 443 must also be open — this is already the case if
  Client Hub is working.)
- **Root / sudo** — the script must run as root. It edits the compose
  file, writes into ``/opt/client-hub/data/``, manipulates iptables,
  and ``apt-get install``s ``iptables-persistent``.
- **You have the target IPs** that need to reach MariaDB. For
  OpsInsights this is::

      52.72.248.4     (AWS NAT Gateway, application traffic)
      52.207.33.249   (OpenVPN server, manual operator traffic)

  These are documented at
  https://connect.opsinsights.com/instructions/index.html

- **OpsInsights enforces SSL client-side** — so the MariaDB cert must
  be trustable. The script uses Caddy's Let's Encrypt cert (publicly
  trusted); no client-side cert-trust config is needed.


**********************************************************************
What the script does, in plain English
**********************************************************************

The script is ``scripts/setup-opsinsights-tls.sh``. Given a hostname
and one-or-more allowed IPs, it:

1. **Adds a Caddyfile site block** for the supplied hostname (e.g.
   ``client-hub.customer.com``). Caddy reloads and acquires a Let's
   Encrypt cert via ACME HTTP-01. The site proxies to the same
   FastAPI as the existing ``onlinesalessystems.com`` block — its
   primary purpose is to produce a valid TLS cert, but it also gives
   you a second hostname you can point integrations at.

2. **Stages the cert for MariaDB** by copying it into
   ``data/mariadb-tls/`` with ownership ``999:999`` (the ``mysql``
   user inside the MariaDB container) and permissions ``0640``
   (cert) / ``0600`` (key). This avoids two problems:

   a. The Caddy data volume is ``0700 root`` — the ``mysql`` user
      can't read it directly.
   b. The Caddy path contains the hostname, which changes per
      customer. A stable copy path means the compose file can be
      templated.

3. **Patches** ``docker-compose.bundled.yml`` (backing up to
   ``.bak-pre-opsinsights``) to:

   - Publish MariaDB on ``3306:3306`` so external clients can reach
     it through the firewall.
   - Bind-mount ``./data/mariadb-tls/`` into the container
     read-only at ``/etc/mysql-tls/``.
   - Pass ``--ssl-cert`` and ``--ssl-key`` as ``mysqld`` command
     arguments so MariaDB serves TLS with the Let's Encrypt cert.

   **The script intentionally does NOT set
   ``--require-secure-transport=ON``** globally. That would reject
   the internal FastAPI container's plain-TCP connection (which runs
   over the ``clienthub`` Docker network, not TLS) and break the
   production conversion-tracking integration. Instead, TLS is
   enforced per-user via ``REQUIRE SSL`` on the ``opsinsights_ro``
   account. Same defense-in-depth, zero risk to the existing
   integration.

4. **Adds iptables rules to the** ``DOCKER-USER`` chain. Docker
   manipulates iptables itself and bypasses UFW, so UFW rules on
   Docker-published ports are ineffective. The ``DOCKER-USER`` chain
   is explicitly provided by Docker as the operator-controlled
   hook that runs **before** Docker's own filter chain. Rules added:

   - ``ACCEPT`` for each ``--allow-ip``.
   - ``DROP`` for everything else with ``dport 3306``.
   - IPv6: blanket ``DROP`` on tcp/3306 (the OpsInsights allowlist
     is IPv4-only).

   Rules persist across reboot via ``iptables-persistent`` (written
   to ``/etc/iptables/rules.v4``).

5. **Recreates the MariaDB container** (``docker compose up -d
   mariadb``) so the new ports, mount, and command args take effect.
   The FastAPI and Caddy containers are untouched.

6. **Creates the read-only MariaDB user** ``opsinsights_ro`` (or the
   name passed via ``--mariadb-user``)::

       CREATE USER 'opsinsights_ro'@'%' IDENTIFIED BY '<32-char>';
       GRANT SELECT ON <DB_NAME>.* TO 'opsinsights_ro'@'%';

   By default, **no** ``REQUIRE SSL`` clause is added — as of 2026-04
   OpsInsights cannot negotiate TLS on its MySQL connection due to a
   hardcoded-ADOdb bug (see ``OpsInsights-Direct-TLS-Plan.rst``). The
   IP allowlist from step 4 + MariaDB auth + read-only grants are
   the primary security boundary in this interim mode. Once the
   OpsInsights ADOdb bug is patched, re-run the script with
   ``--require-ssl`` (or manually ``ALTER USER ... REQUIRE SSL``) to
   restore full defense-in-depth. If the user already exists, the
   script keeps the existing password unless ``--rotate-password``
   is passed.

7. **Writes credentials** to
   ``/opt/client-hub/data/opsinsights_credentials.txt`` (mode 0600,
   root-owned) and prints them to stdout so the operator can copy
   them into OpsInsights.

8. **Verifies** — logs in as ``opsinsights_ro`` over TLS (must
   succeed). The non-TLS behavior depends on whether
   ``--require-ssl`` was passed: without the flag (default / interim
   mode), plaintext login must succeed; with the flag, plaintext
   login must be rejected.


**********************************************************************
Running the script
**********************************************************************

On the Client Hub VPS, as root::

    cd /opt/client-hub
    sudo ./scripts/setup-opsinsights-tls.sh \
        --hostname client-hub.<customer-domain> \
        --allow-ip 52.72.248.4 \
        --allow-ip 52.207.33.249

If Client Hub is installed in a non-default location::

    sudo ./scripts/setup-opsinsights-tls.sh \
        --install-dir /srv/client-hub \
        --hostname client-hub.<customer-domain> \
        --allow-ip 52.72.248.4 \
        --allow-ip 52.207.33.249

To preview without changing anything::

    sudo ./scripts/setup-opsinsights-tls.sh \
        --hostname ... --allow-ip ... --dry-run

To rotate the password for an existing ``opsinsights_ro`` user::

    sudo ./scripts/setup-opsinsights-tls.sh \
        --hostname ... --allow-ip ... --rotate-password

Once OpsInsights is patched to support TLS on MySQL connections,
add ``--require-ssl`` to restore full defense-in-depth::

    sudo ./scripts/setup-opsinsights-tls.sh \
        --hostname ... --allow-ip ... --rotate-password --require-ssl


**********************************************************************
Verification (operator side)
**********************************************************************

Before handing the credentials to OpsInsights, run these on the Client
Hub host::

    # MariaDB listening publicly on 3306
    ss -tlnp | grep :3306
    # expect: 0.0.0.0:3306 LISTEN docker-proxy

    # iptables rules in place
    iptables -L DOCKER-USER -n --line-numbers
    # expect: ACCEPT rows for each allow-ip, then a DROP row

    # Cert matches hostname
    openssl x509 -in /opt/client-hub/data/mariadb-tls/server.crt \
        -noout -subject -issuer -ext subjectAltName
    # expect: CN and SAN = the hostname you passed

    # TLS login works from inside the container
    ROOT_PASS=$(grep ^MARIADB_ROOT_PASSWORD= .env | cut -d= -f2-)
    OPS_PASS=$(grep ^Password: data/opsinsights_credentials.txt | awk '{print $2}')
    docker exec clienthub-mariadb mariadb -h127.0.0.1 \
        -uopsinsights_ro -p"$OPS_PASS" --ssl clienthub \
        -e "SELECT COUNT(*) FROM contacts; STATUS;" \
        | grep -E "Cipher in use|contacts"

From a non-whitelisted host (e.g. a different VPS or workstation)::

    nc -zv client-hub.<customer-domain> 3306
    # expect: timeout / connection refused


**********************************************************************
Verification (OpsInsights side)
**********************************************************************

Hand the operator the credentials printed by the script, then have
them:

1. Create a new client-database record in OpsInsights pointing at
   the printed host/port/db/user/password with ``SSL required``.
2. Run a trivial query, e.g. ``SELECT COUNT(*) FROM contacts;`` —
   must return a row count (not zero unless this truly is a brand
   new install).
3. Attempt a write, e.g. ``INSERT INTO sources (code,name) VALUES
   ('x','y');`` — must be rejected with
   ``ERROR 1142 (42000): INSERT command denied``.

Only after OpsInsights can successfully query AND is correctly
rejected on writes should the work be marked done.


**********************************************************************
Operational notes
**********************************************************************

**Cert renewal.** Caddy auto-renews every ~60 days but MariaDB holds
file handles to the *copy* in ``./data/mariadb-tls/``. After each
Caddy renewal the copy must be refreshed and the MariaDB container
restarted::

    cp data/caddy/caddy/certificates/acme-v02.api.letsencrypt.org-directory/<hostname>/<hostname>.crt \
       data/mariadb-tls/server.crt
    cp data/caddy/caddy/certificates/acme-v02.api.letsencrypt.org-directory/<hostname>/<hostname>.key \
       data/mariadb-tls/server.key
    chown 999:999 data/mariadb-tls/server.crt data/mariadb-tls/server.key
    docker compose -f docker-compose.bundled.yml restart mariadb

TODO: wrap this into ``scripts/refresh-mariadb-tls.sh`` + a systemd
timer (or Caddy ``exec`` hook) so it's automatic. Until then, set a
calendar reminder for ~55 days after each renewal.

**Rotating credentials.** Re-run the script with
``--rotate-password`` to generate a new password for
``opsinsights_ro``. The credentials file is overwritten; update
OpsInsights before the old password is invalidated (the script
drops and recreates the user — there is a brief window, usually
<1s, where both old and new are invalid).

**Removing OpsInsights access.** Revert the changes manually::

    # Revoke MariaDB user
    docker exec -i clienthub-mariadb mariadb -uroot -p<ROOT_PASS> \
        -e "DROP USER 'opsinsights_ro'@'%'; FLUSH PRIVILEGES;"

    # Close firewall
    iptables -D DOCKER-USER -p tcp --dport 3306 -s 52.72.248.4/32 -j ACCEPT
    iptables -D DOCKER-USER -p tcp --dport 3306 -s 52.207.33.249/32 -j ACCEPT
    iptables -D DOCKER-USER -p tcp --dport 3306 -j DROP
    ip6tables -D DOCKER-USER -p tcp --dport 3306 -j DROP
    netfilter-persistent save

    # Restore compose file
    cp docker-compose.bundled.yml.bak-pre-opsinsights docker-compose.bundled.yml
    docker compose -f docker-compose.bundled.yml up -d mariadb

    # Remove Caddyfile block (manual edit) + reload Caddy


**********************************************************************
Security model
**********************************************************************

The access granted by this setup is defense-in-depth:

1. **Network layer** — iptables ``DOCKER-USER`` drops all inbound
   3306 traffic except from the allowlisted IPs. Even if credentials
   leak, an attacker can't open a socket.
2. **TLS layer** — ``REQUIRE SSL`` on the user means MariaDB rejects
   any plain-text connection. Let's Encrypt cert is publicly trusted,
   so clients can verify it without custom CA config.
3. **MariaDB ACL layer** — ``opsinsights_ro`` has ``SELECT`` only on
   the single ``$DB_NAME`` database. No writes, no cross-database
   access, no admin privileges.

Compromise scenarios:

- **Allowlist IP compromised:** attacker can still reach 3306 but
  hits TLS + MariaDB auth. If they also have the password, they
  can SELECT from one database — no writes, no admin. Worst-case
  damage: read-only data exfiltration of that one customer's CRM.
- **Credentials leak:** same as above — allowlist prevents use
  from anywhere else.
- **Both allowlist IP AND credentials compromised:** still
  read-only.
- **MariaDB root compromised:** full damage. Root password is in
  ``.env`` (mode 0600, owned by ``clienthub``). Harden by never
  exposing MariaDB on a path that admits auth as root, which
  this setup ensures (user ``'root'@'localhost'`` only reachable
  via docker exec).

Logical next hardening steps (out of scope here):

- Per-schema view layer so different OpsInsights-driven reports
  can get different grants without sharing one user.
- VPN-only OpsInsights → Client Hub path (SSH tunnel pattern —
  see ``OpsInsights-SSH-Tunnel-Plan.rst``).
- ``audit`` plugin in MariaDB for query logging.


**********************************************************************
When you're done
**********************************************************************

1. Confirm with the operator that OpsInsights can query.
2. Commit any local changes in this repo (the script + these
   docs) in the normal Verify → Document → Commit order.
3. Add a CHANGELOG entry naming the customer and the date.
4. If this is a new customer, update the internal customer
   inventory with the hostname and the OpsInsights connection
   string.
