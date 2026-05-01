"""Tests for canonical IP/UA capture and the IP-aware rate-limit.

The ASGITransport-based test client bypasses uvicorn, so the
``--proxy-headers`` flag does not apply during pytest. We therefore rely on
``body.external_refs_json.ip_address`` (which is the *more trustworthy* source
for source-key endpoints anyway) for end-to-end IP tests, and unit-test
``extract_request_meta`` directly for the X-Forwarded-For / request-peer
fallback path.
"""

from types import SimpleNamespace

import pymysql
import pytest

from app.config import settings
from app.services.request_meta import _is_public_ip, extract_request_meta


def _query(sql: str, params: tuple | None = None):
    conn = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()


def _make_request(*, peer_ip: str | None = "8.8.4.4", ua: str | None = "pytest/1.0"):
    headers = {}
    if ua:
        headers["user-agent"] = ua
    return SimpleNamespace(
        client=SimpleNamespace(host=peer_ip) if peer_ip else None,
        headers=headers,
    )


# =============================================================================
# Helper unit tests
# =============================================================================
def test_is_public_ip_accepts_public_v4():
    # Note: Python's ipaddress.is_private flags the RFC 5737 documentation
    # ranges (192.0.2.x, 198.51.100.x, 203.0.113.x) as private, so we
    # exercise real public IPs here.
    assert _is_public_ip("8.8.8.8") is True
    assert _is_public_ip("1.1.1.1") is True


def test_is_public_ip_rejects_private_loopback_link_local():
    for bad in ("172.18.0.4", "10.0.0.1", "192.168.1.1", "127.0.0.1",
                "169.254.1.1", "::1", "fe80::1", "0.0.0.0", "not-an-ip", ""):
        assert _is_public_ip(bad) is False, bad


def test_extract_request_meta_prefers_payload_public_ip():
    req = _make_request(peer_ip="172.18.0.4", ua="caddy/2")
    refs = {"ip_address": "8.8.8.8", "user_agent": "Mozilla/5.0 RealVisitor"}
    ip, ua = extract_request_meta(req, payload_external_refs=refs)
    assert ip == "8.8.8.8"
    assert ua == "Mozilla/5.0 RealVisitor"


def test_extract_request_meta_falls_back_when_payload_ip_is_private():
    req = _make_request(peer_ip="8.8.4.4", ua="pytest/1.0")
    refs = {"ip_address": "10.0.0.1"}  # private — must be rejected
    ip, ua = extract_request_meta(req, payload_external_refs=refs)
    assert ip == "8.8.4.4"
    assert ua == "pytest/1.0"


def test_extract_request_meta_no_payload_uses_request_peer():
    req = _make_request(peer_ip="9.9.9.9")
    ip, ua = extract_request_meta(req, payload_external_refs=None)
    assert ip == "9.9.9.9"
    assert ua == "pytest/1.0"


def test_extract_request_meta_no_client_no_payload_returns_none():
    req = _make_request(peer_ip=None, ua=None)
    ip, ua = extract_request_meta(req, payload_external_refs=None)
    assert ip is None
    assert ua is None


# =============================================================================
# End-to-end: payload-supplied IP lands in spam_rate_log
# =============================================================================
@pytest.mark.asyncio
async def test_payload_ip_recorded_in_spam_rate_log(client, auth_headers):
    payload_ip = "8.8.4.4"
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Real",
            "last_name": "Visitor",
            "contact_type": "lead",
            "emails": [
                {"address": "real-visitor-uniq1@gmail.com", "type": "personal",
                 "is_primary": True}
            ],
            "phones": [
                {"number": "(555) 222-3344", "type": "mobile", "is_primary": True}
            ],
            "external_refs_json": {
                "ip_address": payload_ip,
                "user_agent": "Mozilla/5.0 (Tester)",
            },
        },
    )
    assert resp.status_code == 201, resp.text

    rows = _query(
        "SELECT key_value, user_agent FROM spam_rate_log "
        "WHERE key_type='ip' AND key_value=%s",
        (payload_ip,),
    )
    assert rows, "expected spam_rate_log row with payload IP"
    assert rows[0][0] == payload_ip
    assert rows[0][1] == "Mozilla/5.0 (Tester)"


@pytest.mark.asyncio
async def test_private_payload_ip_is_rejected_in_favor_of_request_peer(
    client, auth_headers
):
    # If the consumer site mistakenly forwarded a private IP (e.g., its own
    # docker network), we must NOT record it as a public client IP. Helper
    # falls back to the test client's peer (which under ASGITransport is the
    # default httpx client — typically '127.0.0.1' or empty).
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Private",
            "last_name": "IP",
            "contact_type": "lead",
            "emails": [
                {"address": "private-ip-uniq1@gmail.com", "type": "personal",
                 "is_primary": True}
            ],
            "phones": [
                {"number": "(555) 222-9999", "type": "mobile", "is_primary": True}
            ],
            "external_refs_json": {"ip_address": "10.0.0.42"},
        },
    )
    assert resp.status_code == 201

    rows = _query(
        "SELECT key_value FROM spam_rate_log "
        "WHERE key_type='ip' AND key_value='10.0.0.42'"
    )
    assert not rows, "must not record private IP as public client IP"


# =============================================================================
# End-to-end: IP rate-limit kicks in after threshold
# =============================================================================
@pytest.mark.asyncio
async def test_ip_rate_limit_blocks_burst_from_same_ip(client, auth_headers):
    # 5 prior + 1 = 6th request from same IP within 10 min → 6th gets 422.
    burst_ip = "1.1.1.1"
    for i in range(5):
        resp = await client.post(
            "/api/v1/contacts",
            headers=auth_headers,
            json={
                "first_name": "Burst",
                "last_name": f"Tester{i}",
                "contact_type": "lead",
                "emails": [
                    {"address": f"burst-tester-{i}@example.org",
                     "type": "personal", "is_primary": True}
                ],
                "phones": [
                    {"number": f"(555) 333-44{i:02d}", "type": "mobile",
                     "is_primary": True}
                ],
                "external_refs_json": {"ip_address": burst_ip},
            },
        )
        assert resp.status_code == 201, f"request {i} should pass: {resp.text}"

    # 6th request from same IP — different email — should hit the IP rate-limit
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Burst",
            "last_name": "Tester6",
            "contact_type": "lead",
            "emails": [
                {"address": "burst-tester-6@example.org",
                 "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "(555) 333-4406", "type": "mobile",
                 "is_primary": True}
            ],
            "external_refs_json": {"ip_address": burst_ip},
        },
    )
    assert resp.status_code == 422
    rows = _query(
        "SELECT rejection_reason FROM spam_events "
        "WHERE rejection_reason='rate_limit' "
        "ORDER BY occurred_at DESC LIMIT 1"
    )
    assert rows, "expected a rate_limit spam_events row"


# =============================================================================
# End-to-end: Hoff & Mazor pitch is now caught
# =============================================================================
HOFF_AND_MAZOR_BODY = (
    "Hi,\n\nThinking about building a mobile app — or improving the one you "
    "already have?\n\nWe help businesses launch fast, scalable, and "
    "user-friendly apps that actually deliver results.\n\nAt Hoff & Mazor, we "
    "take care of everything from concept to launch — making the process "
    "simple and stress-free for you.\n\nIf you've got an idea (or even just a "
    "goal), let's talk.\n\nOpen to a quick 10-minute chat this week?\n\nBest "
    "regards,\n\nLaura Wheeler\nHoff & Mazor\nlaura.wheeler@hoffandmazoor.com"
    "\n\nRespond with stop to optout."
)


@pytest.mark.asyncio
async def test_hoff_and_mazor_body_is_now_rejected(client, auth_headers):
    """The exact body that slipped through prod on 2026-04-30 must now reject.

    Posted to /communications because that endpoint takes a verbatim body —
    the same path the consumer site uses to log a contact-form message.
    """
    # Need a contact_uuid to attach the communication to — create a dummy.
    create = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "HMTest",
            "last_name": "Target",
            "contact_type": "lead",
            "emails": [
                {"address": "hmtest-target@example.org", "type": "personal",
                 "is_primary": True}
            ],
            "phones": [
                {"number": "(555) 999-1111", "type": "mobile",
                 "is_primary": True}
            ],
            "external_refs_json": {"ip_address": "9.9.9.9"},
        },
    )
    assert create.status_code == 201, create.text
    contact_uuid = create.json()["uuid"]

    resp = await client.post(
        "/api/v1/communications",
        headers=auth_headers,
        json={
            "contact_uuid": contact_uuid,
            "channel": "web_form",
            "direction": "inbound",
            "occurred_at": "2026-05-01T10:00:00",
            "subject": "Contact form (Crowns)",
            "body": HOFF_AND_MAZOR_BODY,
            "external_refs_json": {"ip_address": "4.4.4.4"},
        },
    )
    assert resp.status_code == 422, resp.text

    rows = _query(
        "SELECT rejection_reason, remote_ip FROM spam_events "
        "WHERE rejection_reason='phrase_combo' "
        "ORDER BY occurred_at DESC LIMIT 1"
    )
    assert rows, "expected phrase_combo spam_events row for Hoff & Mazor body"
    assert rows[0][1] == "4.4.4.4", \
        "spam_events.remote_ip must be the payload-supplied client IP, " \
        f"got {rows[0][1]}"
