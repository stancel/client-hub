import uuid

import pytest

ROOT_KEY_HEADERS = {"X-API-Key": "dev-api-key"}


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_create_api_key(client):
    code = _unique("apikey_test")
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "API Key Test"})
    src_uuid = src.json()["uuid"]
    resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Prod key"})
    assert resp.status_code == 201
    data = resp.json()
    assert "key_value" in data
    assert len(data["key_value"]) == 64
    assert data["key_prefix"] == data["key_value"][:8]
    assert "warning" in data


@pytest.mark.asyncio
async def test_list_api_keys(client):
    code = _unique("listkey_test")
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "List Key Test"})
    src_uuid = src.json()["uuid"]
    await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key 1"})
    await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key 2"})
    resp = await client.get(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["count"] >= 2


@pytest.mark.asyncio
async def test_revoke_api_key(client):
    code = _unique("revoke_test")
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Revoke Test"})
    src_uuid = src.json()["uuid"]
    key_resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Revoke"})
    key_uuid = key_resp.json()["uuid"]
    key_value = key_resp.json()["key_value"]

    resp = await client.get("/api/v1/contacts", headers={"X-API-Key": key_value})
    assert resp.status_code == 200

    await client.delete(f"/api/v1/admin/api-keys/{key_uuid}", headers=ROOT_KEY_HEADERS)

    resp = await client.get("/api/v1/contacts", headers={"X-API-Key": key_value})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_source_key_can_read_contacts(client):
    code = _unique("read_test")
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Read Test"})
    src_uuid = src.json()["uuid"]
    key_resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Read"})
    key_value = key_resp.json()["key_value"]
    resp = await client.get("/api/v1/contacts", headers={"X-API-Key": key_value})
    assert resp.status_code == 200
    assert resp.json()["pagination"]["total"] >= 1
