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
) -> tuple[str | None, str | None]:
    """Return ``(client_ip, user_agent)`` using the most trustworthy source.

    Precedence for IP:

    1. ``payload_external_refs["ip_address"]`` if it parses as a public IP.
       This is what consumer Next.js sites send after pulling
       ``CF-Connecting-IP`` server-side.
    2. ``request.client.host`` (uvicorn ``--proxy-headers`` makes this honor
       Caddy's X-Forwarded-For). Returned as-is even for private values, so
       webhook/dev-loop traffic still has *something* recorded.
    3. ``None``.

    Same precedence for User-Agent.
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

    request_ip = request.client.host if request.client else None
    # Drop the request peer too if it's not a public client IP. Private peers
    # show up in two places: (a) docker bridge addresses when --proxy-headers
    # isn't honored (the original bug); (b) ``127.0.0.1`` from the httpx test
    # client. Recording either as the IP rate-limit key bunches all such
    # traffic onto the same row and the rate-limit fires for unrelated calls.
    if request_ip and not _is_public_ip(request_ip):
        request_ip = None
    request_ua = request.headers.get("user-agent")
    if request_ua:
        request_ua = request_ua.strip()[:255] or None

    return (payload_ip or request_ip, payload_ua or request_ua)
