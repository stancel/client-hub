import pytest

ROOT_KEY_HEADERS = {"X-API-Key": "dev-api-key"}


@pytest.mark.asyncio
async def test_list_sources(client):
    resp = await client.get("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    assert any(s["code"] == "bootstrap" for s in data["data"])


@pytest.mark.asyncio
async def test_create_source(client):
    resp = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "test_website",
        "name": "Test Website",
        "source_type": "website",
        "domain": "test.example.com",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "test_website"
    assert "uuid" in data


@pytest.mark.asyncio
async def test_create_source_duplicate_code(client):
    await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "dup_test", "name": "Dup Test",
    })
    resp = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "dup_test", "name": "Dup Test 2",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_source(client):
    create = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "get_test_src", "name": "Get Test",
    })
    uuid = create.json()["uuid"]
    resp = await client.get(f"/api/v1/admin/sources/{uuid}", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["code"] == "get_test_src"


@pytest.mark.asyncio
async def test_update_source(client):
    create = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "upd_test_src", "name": "Update Test",
    })
    uuid = create.json()["uuid"]
    resp = await client.put(f"/api/v1/admin/sources/{uuid}", headers=ROOT_KEY_HEADERS, json={
        "name": "Updated Name",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_source(client):
    create = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "del_test_src", "name": "Delete Test",
    })
    uuid = create.json()["uuid"]
    resp = await client.delete(f"/api/v1/admin/sources/{uuid}", headers=ROOT_KEY_HEADERS)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_admin_requires_root_key(client):
    resp = await client.get("/api/v1/admin/sources")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_rejects_non_root_key(client):
    # Create a source and API key via root
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "reject_test", "name": "Reject Test",
    })
    src_uuid = src.json()["uuid"]
    key_resp = await client.post(f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={
        "name": "test key",
    })
    source_key = key_resp.json()["key_value"]

    # Try to access admin with source key — should get 403
    resp = await client.get("/api/v1/admin/sources", headers={"X-API-Key": source_key})
    assert resp.status_code == 403
