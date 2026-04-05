import pytest


@pytest.mark.asyncio
async def test_list_invoices(client, auth_headers):
    resp = await client.get("/api/v1/invoices", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["pagination"]["total"] >= 3


@pytest.mark.asyncio
async def test_get_invoice(client, auth_headers):
    list_resp = await client.get("/api/v1/invoices", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.get(f"/api/v1/invoices/{uuid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "payments" in data
    assert "balance_due" in data


@pytest.mark.asyncio
async def test_create_invoice_and_record_payment(client, auth_headers):
    # Create an order first
    contacts = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    contact_uuid = contacts.json()["data"][0]["uuid"]

    order = await client.post("/api/v1/orders", headers=auth_headers, json={
        "contact_uuid": contact_uuid, "order_date": "2026-04-05",
        "items": [{"description": "Invoice test", "item_type": "product", "quantity": "1", "unit_price": "100.00"}],
    })
    order_uuid = order.json()["uuid"]

    # Create invoice
    inv_resp = await client.post("/api/v1/invoices", headers=auth_headers, json={
        "order_uuid": order_uuid, "invoice_date": "2026-04-05",
        "subtotal": "100.00", "tax_amount": "8.25",
    })
    assert inv_resp.status_code == 201
    inv_data = inv_resp.json()
    assert inv_data["total"] == "108.25"
    assert inv_data["balance_due"] == "108.25"

    # Record partial payment
    pay_resp = await client.post(f"/api/v1/invoices/{inv_data['uuid']}/payments", headers=auth_headers, json={
        "amount": "50.00", "payment_date": "2026-04-05", "payment_method": "credit_card",
    })
    assert pay_resp.status_code == 201
    assert pay_resp.json()["balance_remaining"] == "58.25"

    # Record final payment
    pay_resp2 = await client.post(f"/api/v1/invoices/{inv_data['uuid']}/payments", headers=auth_headers, json={
        "amount": "58.25", "payment_date": "2026-04-05", "payment_method": "credit_card",
    })
    assert pay_resp2.json()["balance_remaining"] == "0.00"

    # Verify invoice is now paid
    inv_check = await client.get(f"/api/v1/invoices/{inv_data['uuid']}", headers=auth_headers)
    assert inv_check.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_get_invoice_not_found(client, auth_headers):
    resp = await client.get("/api/v1/invoices/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404
