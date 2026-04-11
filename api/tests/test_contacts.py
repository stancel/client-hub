import pytest


@pytest.mark.asyncio
async def test_list_contacts(client, auth_headers):
    resp = await client.get("/api/v1/contacts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["total"] >= 4  # test data has 5 active contacts


@pytest.mark.asyncio
async def test_list_contacts_filter_by_type(client, auth_headers):
    resp = await client.get("/api/v1/contacts?type=client", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    for contact in data["data"]:
        assert contact["contact_type"] == "client"


@pytest.mark.asyncio
async def test_list_contacts_search(client, auth_headers):
    resp = await client.get("/api/v1/contacts?search=Sarah", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["pagination"]["total"] >= 1
    assert any(c["first_name"] == "Sarah" for c in data["data"])


@pytest.mark.asyncio
async def test_get_contact_by_uuid(client, auth_headers):
    # First get the list to find a UUID
    list_resp = await client.get("/api/v1/contacts", headers=auth_headers)
    uuid = list_resp.json()["data"][0]["uuid"]

    resp = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["uuid"] == uuid
    assert "phones" in data
    assert "emails" in data
    assert "tags" in data
    assert "preferences" in data


@pytest.mark.asyncio
async def test_get_contact_not_found(client, auth_headers):
    resp = await client.get("/api/v1/contacts/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_contact(client, auth_headers):
    resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "Test",
        "last_name": "Contact",
        "contact_type": "lead",
        "phones": [{"number": "+15550009999", "type": "mobile", "is_primary": True}],
        "emails": [{"address": "test@example.com", "type": "personal", "is_primary": True}],
        "marketing_sources": ["website"],
        "data_source": "pytest",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "uuid" in data
    assert data["first_name"] == "Test"


@pytest.mark.asyncio
async def test_create_contact_invalid_type(client, auth_headers):
    resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "Bad",
        "last_name": "Type",
        "contact_type": "nonexistent_type",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_contact_missing_name(client, auth_headers):
    resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "contact_type": "lead",
    })
    assert resp.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_contacts_requires_auth(client):
    resp = await client.get("/api/v1/contacts")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_contact_with_external_refs_json(client, auth_headers):
    refs = {
        "source_page": "https://completedentalcarecolumbia.com/book",
        "ip_address": "203.0.113.42",
        "user_agent": "Mozilla/5.0",
    }
    resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "Refs",
        "last_name": "Create",
        "contact_type": "lead",
        "external_refs_json": refs,
    })
    assert resp.status_code == 201
    created = resp.json()
    assert created["external_refs_json"] == refs

    # Round-trip read
    get_resp = await client.get(f"/api/v1/contacts/{created['uuid']}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["external_refs_json"] == refs


@pytest.mark.asyncio
async def test_create_contact_without_external_refs_json(client, auth_headers):
    resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "NoRefs",
        "last_name": "Create",
        "contact_type": "lead",
    })
    assert resp.status_code == 201
    assert resp.json()["external_refs_json"] is None

    uuid = resp.json()["uuid"]
    get_resp = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["external_refs_json"] is None


@pytest.mark.asyncio
async def test_update_contact_external_refs_json(client, auth_headers):
    create_resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "Update",
        "last_name": "Refs",
        "contact_type": "lead",
        "external_refs_json": {"original": True},
    })
    uuid = create_resp.json()["uuid"]

    new_refs = {"replaced": True, "detail": "second value"}
    put_resp = await client.put(
        f"/api/v1/contacts/{uuid}",
        headers=auth_headers,
        json={"external_refs_json": new_refs},
    )
    assert put_resp.status_code == 200

    get_resp = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["external_refs_json"] == new_refs


@pytest.mark.asyncio
async def test_create_contact_external_refs_json_deep_nested(client, auth_headers):
    refs = {
        "source_page": "https://completedentalcarecolumbia.com/book",
        "ip_address": "198.51.100.17",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4)",
        "referrer": "https://google.com",
        "extra": {
            "appointment_id": "apt_abc123",
            "service_name": "Routine Cleaning",
            "staff_name": "Dr. Smith",
            "start_date": "2026-04-20T10:00:00Z",
            "total_price": "150.00",
            "utm_source": "google",
            "utm_medium": "cpc",
        },
    }
    resp = await client.post("/api/v1/contacts", headers=auth_headers, json={
        "first_name": "Deep",
        "last_name": "Nested",
        "contact_type": "lead",
        "external_refs_json": refs,
    })
    assert resp.status_code == 201
    assert resp.json()["external_refs_json"] == refs

    uuid = resp.json()["uuid"]
    get_resp = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert get_resp.status_code == 200
    fetched = get_resp.json()["external_refs_json"]
    assert fetched == refs
    assert fetched["extra"]["appointment_id"] == "apt_abc123"
    assert fetched["extra"]["utm_source"] == "google"
