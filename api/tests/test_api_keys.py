import pytest

ROOT_KEY_HEADERS = {"X-API-Key": "dev-api-key"}


@pytest.mark.asyncio
async def test_create_api_key(client):
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "apikey_test_src", "name": "API Key Test",
    })
    src_uuid = src.json()["uuid"]

    resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={
        "name": "Production key",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "key_value" in data
    assert len(data["key_value"]) == 64  # hex(32) = 64 chars
    assert data["key_prefix"] == data["key_value"][:8]
    assert "warning" in data


@pytest.mark.asyncio
async def test_list_api_keys(client):
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "listkey_test", "name": "List Key Test",
    })
    src_uuid = src.json()["uuid"]

    # Create two keys
    await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key 1"})
    await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key 2"})

    resp = await client.get(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["count"] >= 2


@pytest.mark.asyncio
async def test_revoke_api_key(client):
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "revoke_test", "name": "Revoke Test",
    })
    src_uuid = src.json()["uuid"]

    key_resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={
        "name": "To revoke",
    })
    key_uuid = key_resp.json()["uuid"]
    key_value = key_resp.json()["key_value"]

    # Key works before revocation
    resp = await client.get("/api/v1/contacts", headers={"X-API-Key": key_value})
    assert resp.status_code == 200

    # Revoke
    revoke_resp = await client.delete(f"/api/v1/admin/api-keys/{key_uuid}", headers=ROOT_KEY_HEADERS)
    assert revoke_resp.status_code == 204

    # Key no longer works
    resp = await client.get("/api/v1/contacts", headers={"X-API-Key": key_value})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_source_key_can_read_contacts(client):
    """A source-scoped API key can read all contacts (reads not scoped by source)."""
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "read_test", "name": "Read Test",
    })
    src_uuid = src.json()["uuid"]
    key_resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={
        "name": "Read key",
    })
    key_value = key_resp.json()["key_value"]

    resp = await client.get("/api/v1/contacts", headers={"X-API-Key": key_value})
    assert resp.status_code == 200
    assert resp.json()["pagination"]["total"] >= 1
