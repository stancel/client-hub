import pytest


@pytest.mark.asyncio
async def test_list_communications(client, auth_headers):
    resp = await client.get("/api/v1/communications", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["pagination"]["total"] >= 7


@pytest.mark.asyncio
async def test_list_communications_filter_channel(client, auth_headers):
    resp = await client.get("/api/v1/communications?channel=sms", headers=auth_headers)
    assert resp.status_code == 200
    for comm in resp.json()["data"]:
        assert comm["channel"] == "sms"


@pytest.mark.asyncio
async def test_list_communications_filter_direction(client, auth_headers):
    resp = await client.get("/api/v1/communications?direction=inbound", headers=auth_headers)
    assert resp.status_code == 200
    for comm in resp.json()["data"]:
        assert comm["direction"] == "inbound"


@pytest.mark.asyncio
async def test_create_communication(client, auth_headers):
    contacts = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    contact_uuid = contacts.json()["data"][0]["uuid"]

    resp = await client.post("/api/v1/communications", headers=auth_headers, json={
        "contact_uuid": contact_uuid,
        "channel": "sms",
        "direction": "outbound",
        "occurred_at": "2026-04-05T15:00:00",
        "body": "Test message from pytest",
        "created_by": "pytest",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["channel"] == "sms"
    assert data["direction"] == "outbound"


@pytest.mark.asyncio
async def test_get_communication(client, auth_headers):
    list_resp = await client.get("/api/v1/communications", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.get(f"/api/v1/communications/{uuid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "contact" in data
    assert "channel" in data
    assert "direction" in data


@pytest.mark.asyncio
async def test_get_communication_not_found(client, auth_headers):
    resp = await client.get("/api/v1/communications/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404
