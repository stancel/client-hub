import pytest


@pytest.mark.asyncio
async def test_lookup_phone_found(client, auth_headers):
    resp = await client.get("/api/v1/lookup/phone/+15555550101", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    match = data["matches"][0]
    assert match["first_name"] == "Sarah"
    assert match["last_name"] == "Johnson"
    assert match["contact_type"] == "client"
    assert match["phone"]["number"] == "+15555550101"
    assert match["phone"]["is_primary"] is True


@pytest.mark.asyncio
async def test_lookup_phone_not_found(client, auth_headers):
    resp = await client.get("/api/v1/lookup/phone/+19999999999", headers=auth_headers)
    assert resp.status_code == 404


# Phone normalization (v0.3.0) — caller can pass any common format and
# the lookup endpoint resolves to the same E.164-stored row.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_format",
    [
        "5555550101",          # 10-digit US, no formatting
        "1-555-555-0101",      # 11-digit with leading 1, dashes
        "(555) 555-0101",      # parenthesized
        "555.555.0101",        # dot-separated
    ],
)
async def test_lookup_phone_format_agnostic(client, auth_headers, input_format):
    resp = await client.get(
        f"/api/v1/lookup/phone/{input_format}", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["count"] >= 1
    assert data["matches"][0]["phone"]["number"] == "+15555550101"


@pytest.mark.asyncio
async def test_lookup_phone_returns_recent_orders(client, auth_headers):
    resp = await client.get("/api/v1/lookup/phone/+15555550101", headers=auth_headers)
    data = resp.json()
    match = data["matches"][0]
    assert len(match["recent_orders"]) > 0
    assert "order_number" in match["recent_orders"][0]


@pytest.mark.asyncio
async def test_lookup_phone_returns_tags(client, auth_headers):
    resp = await client.get("/api/v1/lookup/phone/+15555550101", headers=auth_headers)
    data = resp.json()
    match = data["matches"][0]
    assert "VIP Customer" in match["tags"]


@pytest.mark.asyncio
async def test_lookup_phone_returns_channel_prefs(client, auth_headers):
    resp = await client.get("/api/v1/lookup/phone/+15555550101", headers=auth_headers)
    data = resp.json()
    match = data["matches"][0]
    assert "sms" in match["channel_preferences"]
    assert match["channel_preferences"]["sms"]["preferred"] is True


@pytest.mark.asyncio
async def test_lookup_email_found(client, auth_headers):
    resp = await client.get(
        "/api/v1/lookup/email/dr.chen@dallasdental.example.com",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    match = data["matches"][0]
    assert match["first_name"] == "Dr. Michael"
    assert match["contact_type"] == "prospect"


@pytest.mark.asyncio
async def test_lookup_email_not_found(client, auth_headers):
    resp = await client.get("/api/v1/lookup/email/nobody@nowhere.com", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_lookup_requires_auth(client):
    resp = await client.get("/api/v1/lookup/phone/+15555550101")
    assert resp.status_code == 401
