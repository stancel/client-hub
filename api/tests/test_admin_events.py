import pytest

ROOT_KEY_HEADERS = {"X-API-Key": "dev-api-key"}


@pytest.mark.asyncio
async def test_list_events(client):
    resp = await client.get("/api/v1/admin/events", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "count" in data


@pytest.mark.asyncio
async def test_list_events_filter_by_channel(client):
    resp = await client.get("/api/v1/admin/events?channel_code=sms", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    for event in resp.json()["data"]:
        assert event["channel_code"] == "sms"


@pytest.mark.asyncio
async def test_list_events_filter_by_date(client):
    resp = await client.get(
        "/api/v1/admin/events?date_from=2026-01-01&date_to=2026-12-31",
        headers=ROOT_KEY_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_events_requires_root_key(client):
    resp = await client.get("/api/v1/admin/events")
    assert resp.status_code == 401
