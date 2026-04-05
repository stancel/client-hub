import pytest


@pytest.mark.asyncio
async def test_get_marketing_optouts(client, auth_headers):
    list_resp = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.get(f"/api/v1/contacts/{uuid}/marketing", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "opt_out_sms" in data
    assert "opt_out_email" in data
    assert "opt_out_phone" in data


@pytest.mark.asyncio
async def test_update_marketing_optouts(client, auth_headers):
    list_resp = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.put(f"/api/v1/contacts/{uuid}/marketing", headers=auth_headers, json={
        "opt_out_sms": True,
        "opt_out_email": False,
        "opt_out_phone": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["opt_out_sms"] is True
    assert data["opt_out_email"] is False
    assert data["opt_out_phone"] is True

    # Verify it persisted
    verify = await client.get(f"/api/v1/contacts/{uuid}/marketing", headers=auth_headers)
    assert verify.json()["opt_out_sms"] is True


@pytest.mark.asyncio
async def test_marketing_optouts_not_found(client, auth_headers):
    resp = await client.get("/api/v1/contacts/00000000-0000-0000-0000-000000000000/marketing", headers=auth_headers)
    assert resp.status_code == 404
