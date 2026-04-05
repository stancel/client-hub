import pytest


@pytest.mark.asyncio
async def test_invoiceninja_payment_webhook(client, auth_headers):
    resp = await client.post("/api/v1/webhooks/invoiceninja", headers=auth_headers, json={
        "event": "payment.created",
        "data": {
            "invoice_id": "NINJA-INV-10001",
            "amount": 10.00,
            "payment_id": "NINJA-PAY-99999",
        },
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["event"] == "payment.created"


@pytest.mark.asyncio
async def test_invoiceninja_unknown_event(client, auth_headers):
    resp = await client.post("/api/v1/webhooks/invoiceninja", headers=auth_headers, json={
        "event": "unknown.event",
        "data": {},
    })
    assert resp.status_code == 200
    assert resp.json()["event"] == "unknown.event"


@pytest.mark.asyncio
async def test_invoiceninja_webhook_requires_auth(client):
    resp = await client.post("/api/v1/webhooks/invoiceninja", json={"event": "test", "data": {}})
    assert resp.status_code == 401
