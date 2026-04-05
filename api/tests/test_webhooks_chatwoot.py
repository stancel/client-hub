import pytest


@pytest.mark.asyncio
async def test_chatwoot_message_known_contact(client, auth_headers):
    resp = await client.post("/api/v1/webhooks/chatwoot", headers=auth_headers, json={
        "event": "message_created",
        "data": {
            "id": "CW-TEST-001",
            "content": "Hi, I have a question about my order",
            "sender": {"phone_number": "+15555550101"},
        },
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert any("communication logged" in p for p in data["processed"])


@pytest.mark.asyncio
async def test_chatwoot_message_unknown_contact(client, auth_headers):
    resp = await client.post("/api/v1/webhooks/chatwoot", headers=auth_headers, json={
        "event": "message_created",
        "data": {
            "id": "CW-TEST-002",
            "content": "Hello from unknown",
            "sender": {"phone_number": "+19999999999"},
        },
    })
    assert resp.status_code == 200
    assert "contact not identified" in resp.json()["processed"]


@pytest.mark.asyncio
async def test_chatwoot_message_by_email(client, auth_headers):
    resp = await client.post("/api/v1/webhooks/chatwoot", headers=auth_headers, json={
        "event": "message_created",
        "data": {
            "id": "CW-TEST-003",
            "content": "Email-based inquiry",
            "sender": {"email": "sarah.johnson@example.com"},
        },
    })
    assert resp.status_code == 200
    assert any("communication logged" in p for p in resp.json()["processed"])


@pytest.mark.asyncio
async def test_chatwoot_webhook_requires_auth(client):
    resp = await client.post("/api/v1/webhooks/chatwoot", json={"event": "test", "data": {}})
    assert resp.status_code == 401
