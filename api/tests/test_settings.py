import pytest


@pytest.mark.asyncio
async def test_get_settings(client, auth_headers):
    resp = await client.get("/api/v1/settings", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["business_name"] == "Stitch & Style Embroidery"
    assert data["business_type"] == "embroidery"
    assert data["currency"] == "USD"
    assert "address" in data


@pytest.mark.asyncio
async def test_update_settings(client, auth_headers):
    resp = await client.put("/api/v1/settings", headers=auth_headers, json={
        "phone": "555-555-9999",
    })
    assert resp.status_code == 200

    # Verify
    check = await client.get("/api/v1/settings", headers=auth_headers)
    assert check.json()["phone"] == "555-555-9999"

    # Restore
    await client.put("/api/v1/settings", headers=auth_headers, json={"phone": "555-555-0100"})


@pytest.mark.asyncio
async def test_settings_requires_auth(client):
    resp = await client.get("/api/v1/settings")
    assert resp.status_code == 401
