import uuid

import pytest

ROOT_KEY_HEADERS = {"X-API-Key": "dev-api-key"}


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_list_sources(client):
    resp = await client.get("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    assert any(s["code"] == "bootstrap" for s in data["data"])


@pytest.mark.asyncio
async def test_create_source(client):
    code = _unique("test_website")
    resp = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": code, "name": "Test Website", "source_type": "website", "domain": "test.example.com",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == code
    assert "uuid" in data


@pytest.mark.asyncio
async def test_create_source_duplicate_code(client):
    code = _unique("dup_test")
    await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Dup 1"})
    resp = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Dup 2"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_source(client):
    code = _unique("get_test")
    create = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Get Test"})
    uuid_val = create.json()["uuid"]
    resp = await client.get(f"/api/v1/admin/sources/{uuid_val}", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["code"] == code


@pytest.mark.asyncio
async def test_update_source(client):
    code = _unique("upd_test")
    create = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Upd Test"})
    uuid_val = create.json()["uuid"]
    resp = await client.put(f"/api/v1/admin/sources/{uuid_val}", headers=ROOT_KEY_HEADERS, json={"name": "Updated"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_source(client):
    code = _unique("del_test")
    create = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Del Test"})
    uuid_val = create.json()["uuid"]
    resp = await client.delete(f"/api/v1/admin/sources/{uuid_val}", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_admin_requires_root_key(client):
    resp = await client.get("/api/v1/admin/sources")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_rejects_non_root_key(client):
    code = _unique("reject_test")
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Reject Test"})
    src_uuid = src.json()["uuid"]
    key_resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "test"})
    source_key = key_resp.json()["key_value"]
    resp = await client.get("/api/v1/admin/sources", headers={"X-API-Key": source_key})
    assert resp.status_code == 403
