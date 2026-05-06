"""Tests for /communications endpoint pulling parent-contact email + IP.

Driven by the v0.3.6 CDC breakthrough — the spam_event for the comm
showed submitted_email = NULL because the comm payload itself doesn't
carry email, and remote_ip was the proxy droplet because the consumer
site doesn't include external_refs_json on the comm call. Both fall
back to the parent contact now.
"""

import pymysql
import pytest

from app.config import settings


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


@pytest.mark.asyncio
async def test_comm_uses_parent_contact_email_in_spam_event(client, auth_headers):
    """A graze-but-clean comm body must record the parent's email on
    the soft_signal spam_events row (was NULL before v0.4.0)."""
    create = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Parent",
            "last_name": "Lookup",
            "contact_type": "lead",
            "emails": [
                {"address": "parent-lookup@example.org", "type": "personal",
                 "is_primary": True}
            ],
            "phones": [
                {"number": "(212) 555-0145", "type": "mobile",
                 "is_primary": True}
            ],
            "external_refs_json": {"ip_address": "9.9.9.9"},
        },
    )
    assert create.status_code == 201, create.text
    contact_uuid = create.json()["uuid"]

    # Body contains a single-phrase graze ("Hello Good Morning,") so the
    # comm passes (below 2-match threshold) but writes a soft_signal event.
    resp = await client.post(
        "/api/v1/communications",
        headers=auth_headers,
        json={
            "contact_uuid": contact_uuid,
            "channel": "web_form",
            "direction": "inbound",
            "occurred_at": "2026-05-06T10:00:00",
            "subject": "Inquiry",
            "body": "Hello Good Morning, I'm interested in your services.",
        },
    )
    assert resp.status_code == 201, resp.text

    rows = _query(
        "SELECT submitted_email, remote_ip, peer_ip, rejection_reason "
        "FROM spam_events "
        "WHERE endpoint='/api/v1/communications' "
        "AND rejection_reason='soft_signal' "
        "ORDER BY occurred_at DESC LIMIT 1"
    )
    assert rows, "expected soft_signal spam_events row"
    submitted_email, remote_ip, _peer_ip, reason = rows[0]
    assert reason == "soft_signal"
    assert submitted_email == "parent-lookup@example.org", \
        "comm endpoint must look up parent contact's email"
    # Comm payload had no external_refs_json — fallback should pull from
    # the contact's stored ip_address (9.9.9.9).
    assert remote_ip == "9.9.9.9", \
        "comm spam_event must use parent contact's stored IP as fallback"


@pytest.mark.asyncio
async def test_comm_payload_ip_overrides_parent_fallback(client, auth_headers):
    """When the comm explicitly carries external_refs_json.ip_address,
    that must win over the parent-contact fallback."""
    create = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Override",
            "last_name": "Test",
            "contact_type": "lead",
            "emails": [
                {"address": "override-test@example.org", "type": "personal",
                 "is_primary": True}
            ],
            "phones": [
                {"number": "(212) 555-0146", "type": "mobile",
                 "is_primary": True}
            ],
            "external_refs_json": {"ip_address": "9.9.9.9"},
        },
    )
    contact_uuid = create.json()["uuid"]

    resp = await client.post(
        "/api/v1/communications",
        headers=auth_headers,
        json={
            "contact_uuid": contact_uuid,
            "channel": "web_form",
            "direction": "inbound",
            "occurred_at": "2026-05-06T10:00:01",
            "subject": "Inquiry",
            "body": "Hello Good Morning, follow-up question.",
            "external_refs_json": {"ip_address": "8.8.4.20"},
        },
    )
    assert resp.status_code == 201, resp.text

    # Confirm rate-log captured the comm-payload IP, not the parent-contact
    # fallback. (No spam_event is written on a clean comm — by design — so
    # we verify rate-log instead.)
    rows = _query(
        "SELECT key_value FROM spam_rate_log "
        "WHERE key_type='ip' AND key_value='8.8.4.20'"
    )
    assert rows, "comm payload IP must override parent fallback in rate-log"
