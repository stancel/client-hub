import pytest


@pytest.mark.asyncio
async def test_convert_prospect_to_client(client, auth_headers):
    # Create a prospect first
    create_resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "Convert",
        "last_name": "Test",
        "contact_type": "prospect",
    })
    uuid = create_resp.json()["uuid"]

    resp = await client.post(f"/api/v1/contacts/{uuid}/convert", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["contact_type"] == "client"
    assert data["converted_at"] is not None


@pytest.mark.asyncio
async def test_convert_already_client(client, auth_headers):
    # Create a client
    create_resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "Already",
        "last_name": "Client",
        "contact_type": "client",
    })
    uuid = create_resp.json()["uuid"]

    resp = await client.post(f"/api/v1/contacts/{uuid}/convert", headers=auth_headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_convert_not_found(client, auth_headers):
    resp = await client.post(
        "/api/v1/contacts/00000000-0000-0000-0000-000000000000/convert",
        headers=auth_headers,
    )
    assert resp.status_code == 404
