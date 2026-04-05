import pytest


@pytest.mark.asyncio
async def test_list_organizations(client, auth_headers):
    resp = await client.get("/api/v1/organizations", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["pagination"]["total"] >= 2


@pytest.mark.asyncio
async def test_get_organization(client, auth_headers):
    list_resp = await client.get("/api/v1/organizations", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.get(f"/api/v1/organizations/{uuid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["uuid"] == uuid
    assert "phones" in data
    assert "emails" in data
    assert "addresses" in data
    assert "contact_count" in data


@pytest.mark.asyncio
async def test_create_organization(client, auth_headers):
    resp = await client.post("/api/v1/organizations", headers=auth_headers, json={
        "name": "Test Corp", "org_type": "company", "website": "https://test.example.com",
    })
    assert resp.status_code == 201
    assert "uuid" in resp.json()


@pytest.mark.asyncio
async def test_update_organization(client, auth_headers):
    create_resp = await client.post("/api/v1/organizations", headers=auth_headers, json={"name": "Update Corp"})
    uuid = create_resp.json()["uuid"]

    resp = await client.put(f"/api/v1/organizations/{uuid}", headers=auth_headers, json={"name": "Updated Corp"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_organization(client, auth_headers):
    create_resp = await client.post("/api/v1/organizations", headers=auth_headers, json={"name": "Delete Corp"})
    uuid = create_resp.json()["uuid"]

    resp = await client.delete(f"/api/v1/organizations/{uuid}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_get_organization_not_found(client, auth_headers):
    resp = await client.get("/api/v1/organizations/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404
