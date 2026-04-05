import pytest


@pytest.mark.asyncio
async def test_list_preferences(client, auth_headers):
    list_resp = await client.get("/api/v1/contacts?search=Sarah", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.get(f"/api/v1/contacts/{uuid}/preferences", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(p["key"] == "preferred_contact_time" for p in data)


@pytest.mark.asyncio
async def test_set_preference(client, auth_headers):
    list_resp = await client.get("/api/v1/contacts?search=Sarah", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.put(
        f"/api/v1/contacts/{uuid}/preferences/test_key",
        headers=auth_headers,
        json={"value": "test_value", "data_source": "pytest"},
    )
    assert resp.status_code == 200
    assert resp.json()["key"] == "test_key"
    assert resp.json()["value"] == "test_value"


@pytest.mark.asyncio
async def test_update_existing_preference(client, auth_headers):
    list_resp = await client.get("/api/v1/contacts?search=Sarah", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    # Set
    await client.put(
        f"/api/v1/contacts/{uuid}/preferences/update_test",
        headers=auth_headers,
        json={"value": "v1"},
    )
    # Update
    resp = await client.put(
        f"/api/v1/contacts/{uuid}/preferences/update_test",
        headers=auth_headers,
        json={"value": "v2"},
    )
    assert resp.json()["value"] == "v2"


@pytest.mark.asyncio
async def test_delete_preference(client, auth_headers):
    list_resp = await client.get("/api/v1/contacts?search=Sarah", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    # Create it first
    await client.put(
        f"/api/v1/contacts/{uuid}/preferences/delete_me",
        headers=auth_headers,
        json={"value": "temp"},
    )

    resp = await client.delete(f"/api/v1/contacts/{uuid}/preferences/delete_me", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_preference_not_found(client, auth_headers):
    list_resp = await client.get("/api/v1/contacts?search=Sarah", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.delete(f"/api/v1/contacts/{uuid}/preferences/nonexistent", headers=auth_headers)
    assert resp.status_code == 404
