"""Request-meta extraction — canonical client IP and User-Agent.

The trust model:

- For source-key-authenticated ingest (consumer-site contact forms, booking
  forms, scheduler webhooks), the consumer-site server already extracts the
  real visitor IP from Cloudflare's CF-Connecting-IP and embeds it in
  ``body.external_refs_json.ip_address``. That value is **more trustworthy**
  than X-Forwarded-For at our edge, because X-Forwarded-For only tells us the
  consumer-site server's egress IP.
- For other traffic (Chatwoot/InvoiceNinja webhooks, direct admin API), the
  X-Forwarded-For chain populated by uvicorn's ``--proxy-headers`` option (set
  in the Dockerfile) is the canonical source. ``request.client.host`` gives
  us the right value once that flag is on.

Anything that builds an ``IntakePayload`` for the spam filter — and any other
ingest adapter that wants to record IP/UA — must go through this helper. See
docs/Spam-Defense-Pattern.rst for the broader inheritance pattern.
"""

from __future__ import annotations

import ipaddress
from typing import Any

from fastapi import Request


def _is_public_ip(value: str | None) -> bool:
    if not value:
        return False
    try:
        ip = ipaddress.ip_address(value.strip())
    except (TypeError, ValueError):
        return False
    # Reject only addresses that *cannot* legitimately be a remote client:
    # private (RFC 1918), loopback (127.x), link-local (169.254.x) and
    # unspecified (0.0.0.0). We deliberately accept ``is_reserved`` because
    # that includes RFC 5737 documentation ranges (203.0.113.x etc.) which
    # are valid in tests, and accept ``is_multicast`` for the same reason —
    # if a real spammer used a multicast source IP we'd want to record it.
    return not (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_unspecified)


def extract_request_meta(
    request: Request,
    *,
    payload_external_refs: dict[str, Any] | None = None,
) -> tuple[str | None, str | None, str | None]:
    """Return ``(canonical_ip, peer_ip, user_agent)``.

    Two distinct IP notions are returned so callers can record both in
    ``spam_events`` and never confuse "where the visitor came from" with
    "what hit our edge":

    - ``canonical_ip`` — best-known public *visitor* IP. Used for rate-
      limit keying and the ``spam_events.remote_ip`` audit column.
      Precedence: ``payload_external_refs["ip_address"]`` if public →
      ``request.client.host`` if public → ``None``.
    - ``peer_ip`` — raw TCP peer (``request.client.host``), kept even
      if private/loopback. Recorded to ``spam_events.peer_ip`` for
      forensics, never used for rate-limit keying. Tells us whether
      a submission relayed through one of our consumer-site droplets
      vs. came direct.
    - ``user_agent`` — payload UA → request UA → ``None``.

    The split fixes a v0.3.6 bug where the consumer-site droplet IP
    landed in ``remote_ip`` because the comm payload didn't carry
    ``ip_address``. Now even in that case ``canonical_ip`` is None
    (caller falls back to parent-contact lookup) and ``peer_ip``
    captures the droplet for forensics.
    """
    payload_ip: str | None = None
    payload_ua: str | None = None
    if payload_external_refs:
        raw_ip = payload_external_refs.get("ip_address")
        if isinstance(raw_ip, str) and _is_public_ip(raw_ip):
            payload_ip = raw_ip.strip()
        raw_ua = payload_external_refs.get("user_agent")
        if isinstance(raw_ua, str) and raw_ua.strip():
            payload_ua = raw_ua.strip()[:255]

    raw_peer = request.client.host if request.client else None
    peer_ip = raw_peer.strip() if raw_peer else None

    # canonical IP excludes private/loopback peers — those are docker
    # bridge addresses or test-client localhost, never a real visitor.
    canonical_request_ip = peer_ip if peer_ip and _is_public_ip(peer_ip) else None

    request_ua = request.headers.get("user-agent")
    if request_ua:
        request_ua = request_ua.strip()[:255] or None

    return (
        payload_ip or canonical_request_ip,
        peer_ip,
        payload_ua or request_ua,
    )
