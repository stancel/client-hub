import pytest


@pytest.mark.asyncio
async def test_list_orders(client, auth_headers):
    resp = await client.get("/api/v1/orders", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["pagination"]["total"] >= 4


@pytest.mark.asyncio
async def test_list_orders_filter_by_status(client, auth_headers):
    resp = await client.get("/api/v1/orders?status=completed", headers=auth_headers)
    assert resp.status_code == 200
    for order in resp.json()["data"]:
        assert order["status"] == "completed"


@pytest.mark.asyncio
async def test_get_order(client, auth_headers):
    list_resp = await client.get("/api/v1/orders", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.get(f"/api/v1/orders/{uuid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "status_history" in data
    assert "contact" in data


@pytest.mark.asyncio
async def test_create_order_with_items(client, auth_headers):
    # Get a contact UUID
    contacts = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    contact_uuid = contacts.json()["data"][0]["uuid"]

    resp = await client.post("/api/v1/orders", headers=auth_headers, json={
        "contact_uuid": contact_uuid,
        "order_date": "2026-04-05",
        "items": [
            {"description": "Test product", "item_type": "product", "quantity": "2.00", "unit_price": "25.00"},
            {"description": "Test service", "item_type": "service", "quantity": "1.00", "unit_price": "50.00"},
        ],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "uuid" in data
    assert data["total"] == "100.00"  # (2*25) + (1*50)


@pytest.mark.asyncio
async def test_change_order_status(client, auth_headers):
    contacts = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    contact_uuid = contacts.json()["data"][0]["uuid"]

    create = await client.post("/api/v1/orders", headers=auth_headers, json={
        "contact_uuid": contact_uuid, "order_date": "2026-04-05",
        "items": [{"description": "Status test", "item_type": "product", "quantity": "1", "unit_price": "10.00"}],
    })
    uuid = create.json()["uuid"]

    resp = await client.post(f"/api/v1/orders/{uuid}/status", headers=auth_headers, json={
        "status": "confirmed", "changed_by": "pytest",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_get_order_not_found(client, auth_headers):
    resp = await client.get("/api/v1/orders/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_order_invalid_contact(client, auth_headers):
    resp = await client.post("/api/v1/orders", headers=auth_headers, json={
        "contact_uuid": "00000000-0000-0000-0000-000000000000", "order_date": "2026-04-05",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_order_with_external_refs_json(client, auth_headers):
    contacts = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    contact_uuid = contacts.json()["data"][0]["uuid"]

    refs = {
        "eaglesoft_chart": "A-1234",
        "booking": {"source": "web", "slot": "morning"},
    }
    resp = await client.post("/api/v1/orders", headers=auth_headers, json={
        "contact_uuid": contact_uuid,
        "order_date": "2026-04-05",
        "items": [{"description": "Refs item", "item_type": "product", "quantity": "1", "unit_price": "10.00"}],
        "external_refs_json": refs,
    })
    assert resp.status_code == 201
    assert resp.json()["external_refs_json"] == refs

    uuid = resp.json()["uuid"]
    get_resp = await client.get(f"/api/v1/orders/{uuid}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["external_refs_json"] == refs
