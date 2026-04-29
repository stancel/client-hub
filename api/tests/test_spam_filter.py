"""Tests for the spam-defense framework.

Covers:
  - Public source-key gated GET /api/v1/spam-patterns
  - Admin CRUD on /api/v1/admin/spam-patterns
  - Admin events list / stats / mark-false-positive
  - Spam guard wired into POST /contacts (rejection paths)
  - Mark-false-positive flow + pattern false_positive_count bump
"""

import pytest


# =============================================================================
# Public read — source-key gated
# =============================================================================
@pytest.mark.asyncio
async def test_get_spam_patterns_grouped_requires_auth(client):
    resp = await client.get("/api/v1/spam-patterns")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_spam_patterns_grouped_returns_canonical_lists(client, auth_headers):
    resp = await client.get("/api/v1/spam-patterns", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    # All 5 pattern kinds must be present, each as a list
    for kind in (
        "email_substring", "full_email_block", "url_regex",
        "phrase_regex", "phone_country_block",
    ):
        assert kind in data
        assert isinstance(data[kind], list)
    # Migration 023 seeds at least 13 email_substring + 7 url_regex + 13 phrase_regex
    assert len(data["email_substring"]) >= 13
    assert len(data["url_regex"]) >= 7
    assert len(data["phrase_regex"]) >= 13


# =============================================================================
# Admin pattern CRUD
# =============================================================================
@pytest.mark.asyncio
async def test_admin_list_patterns(client, auth_headers):
    resp = await client.get("/api/v1/admin/spam-patterns", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data and "pagination" in data
    assert data["pagination"]["total"] > 30  # seeded patterns


@pytest.mark.asyncio
async def test_admin_create_and_update_and_delete_pattern(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/admin/spam-patterns",
        headers=auth_headers,
        json={
            "pattern_kind": "email_substring",
            "pattern": "test_marker_xyzzy",
            "notes": "test pattern from pytest",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    uuid = create_resp.json()["uuid"]
    assert create_resp.json()["is_active"] is True

    update_resp = await client.put(
        f"/api/v1/admin/spam-patterns/{uuid}",
        headers=auth_headers,
        json={"is_active": False, "notes": "disabled by test"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["is_active"] is False
    assert update_resp.json()["notes"] == "disabled by test"

    delete_resp = await client.delete(
        f"/api/v1/admin/spam-patterns/{uuid}", headers=auth_headers
    )
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_admin_create_pattern_invalid_regex(client, auth_headers):
    resp = await client.post(
        "/api/v1/admin/spam-patterns",
        headers=auth_headers,
        json={"pattern_kind": "url_regex", "pattern": "(unbalanced"},
    )
    assert resp.status_code == 400
    assert "Invalid regex" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_admin_update_pattern_not_found(client, auth_headers):
    resp = await client.put(
        "/api/v1/admin/spam-patterns/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
        json={"notes": "x"},
    )
    assert resp.status_code == 404


# =============================================================================
# Spam guard — rejection paths via POST /contacts
# =============================================================================
@pytest.mark.asyncio
async def test_contact_create_rejected_for_blocked_email_substring(client, auth_headers):
    # 'webdigital' is a seeded email_substring pattern
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Spam",
            "last_name": "Bot",
            "contact_type": "lead",
            "emails": [
                {"address": "anyone@badwebdigital.com", "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "+15555550101", "type": "mobile", "is_primary": True}
            ],
        },
    )
    assert resp.status_code == 422
    # Generic reject message — no rule leakage
    assert "Submission rejected" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_contact_create_rejected_for_invalid_phone_too_many_digits(client, auth_headers):
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Cameroon",
            "last_name": "Mill",
            "contact_type": "lead",
            "emails": [
                {"address": "harmless@example.org", "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "+235689505412", "type": "mobile", "is_primary": True}
            ],
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_contact_create_rejected_for_country_code_block(client, auth_headers):
    # +235 is a seeded phone_country_block pattern. With "+235 6 89 50 54" the
    # digits collapse to 10 (which would *pass* phone_invalid digit-count), so
    # the country-code substring pattern is what catches it.
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Country",
            "last_name": "Block",
            "contact_type": "lead",
            "emails": [
                {"address": "harmless2@example.org", "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "+235 6 89 50 54", "type": "mobile", "is_primary": True}
            ],
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_contact_create_clean_payload_succeeds(client, auth_headers):
    """A real-looking submission must NOT be flagged as spam."""
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Real",
            "last_name": "Customer",
            "contact_type": "lead",
            "emails": [
                {"address": "real.customer@gmail.com", "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "(555) 123-4567", "type": "mobile", "is_primary": True}
            ],
        },
    )
    assert resp.status_code == 201, resp.text


# =============================================================================
# Spam events — admin list / stats / mark-false-positive
# =============================================================================
@pytest.mark.asyncio
async def test_admin_spam_events_list_after_rejection(client, auth_headers):
    # Trigger one rejection to populate spam_events
    await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "EventGen",
            "last_name": "Spam",
            "contact_type": "lead",
            "emails": [
                {"address": "x@websolutionprobe.com", "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "5551239999", "type": "mobile", "is_primary": True}
            ],
        },
    )

    resp = await client.get(
        "/api/v1/admin/spam-events?endpoint=/api/v1/contacts&per_page=10",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pagination"]["total"] >= 1
    # The most recent event should match what we just submitted
    most_recent = data["data"][0]
    assert most_recent["endpoint"] == "/api/v1/contacts"
    assert most_recent["integration_kind"] == "web_form"
    assert most_recent["rejection_reason"] in (
        "email_blocked", "phone_invalid", "url_blocked", "phrase_combo", "rate_limit",
    )
    assert most_recent["was_false_positive"] is False


@pytest.mark.asyncio
async def test_admin_spam_events_stats(client, auth_headers):
    resp = await client.get(
        "/api/v1/admin/spam-events/stats", headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_events" in data
    assert "by_endpoint" in data
    assert "by_pattern" in data
    assert "by_ip_top" in data
    assert isinstance(data["by_endpoint"], list)


@pytest.mark.asyncio
async def test_admin_mark_false_positive_bumps_pattern_counter(client, auth_headers):
    # 1) Trigger a rejection caused by a pattern we control so we can verify
    #    the counter on it.
    create_pat = await client.post(
        "/api/v1/admin/spam-patterns",
        headers=auth_headers,
        json={
            "pattern_kind": "email_substring",
            "pattern": "fp_test_marker",
            "notes": "false-positive test pattern",
        },
    )
    pat_uuid = create_pat.json()["uuid"]

    # Trigger a rejection that this pattern matches
    await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "FP",
            "last_name": "Test",
            "contact_type": "lead",
            "emails": [
                {"address": "x@fp_test_marker.com", "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "5551231234", "type": "mobile", "is_primary": True}
            ],
        },
    )

    # Find the event we just generated
    events = (await client.get(
        "/api/v1/admin/spam-events?submitted_email=x@fp_test_marker.com",
        headers=auth_headers,
    )).json()
    assert events["pagination"]["total"] >= 1
    event_uuid = events["data"][0]["uuid"]

    # Mark as false positive
    fp_resp = await client.post(
        f"/api/v1/admin/spam-events/{event_uuid}/mark-false-positive",
        headers=auth_headers,
    )
    assert fp_resp.status_code == 200
    assert fp_resp.json()["was_false_positive"] is True

    # Pattern's false_positive_count must have incremented
    pat_after = (await client.get(
        "/api/v1/admin/spam-patterns?per_page=200", headers=auth_headers,
    )).json()
    matching = [p for p in pat_after["data"] if p["uuid"] == pat_uuid]
    assert len(matching) == 1
    assert matching[0]["false_positive_count"] >= 1

    # Cleanup the test pattern
    await client.delete(
        f"/api/v1/admin/spam-patterns/{pat_uuid}", headers=auth_headers,
    )
