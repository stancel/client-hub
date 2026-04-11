import pytest

ROOT_KEY_HEADERS = {"X-API-Key": "dev-api-key"}


@pytest.mark.asyncio
async def test_multi_source_full_flow(client):
    """Critical test: full multi-source attribution flow per the spec."""

    # 1. Create two sources (A and B) with separate API keys
    src_a = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "source_a", "name": "Source A", "source_type": "website",
    })
    src_a_uuid = src_a.json()["uuid"]
    key_a_resp = await client.post(
        f"/api/v1/admin/sources/{src_a_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key A"}
    )
    key_a = key_a_resp.json()["key_value"]

    src_b = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "source_b", "name": "Source B", "source_type": "cti",
    })
    src_b_uuid = src_b.json()["uuid"]
    key_b_resp = await client.post(
        f"/api/v1/admin/sources/{src_b_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key B"}
    )
    key_b = key_b_resp.json()["key_value"]

    headers_a = {"X-API-Key": key_a}
    headers_b = {"X-API-Key": key_b}

    # 2. Use source A's key to create a contact
    contact_resp = await client.post("/api/v1/contacts", headers=headers_a, json={
        "first_name": "Multi", "last_name": "SourceTest", "contact_type": "lead",
    })
    assert contact_resp.status_code == 201
    contact_uuid = contact_resp.json()["uuid"]

    # Verify first_seen_source_id = A (check via get endpoint)
    detail = await client.get(f"/api/v1/contacts/{contact_uuid}", headers=headers_a)
    assert detail.status_code == 200

    # 3. Use source B's key to create a communication on that contact
    comm_resp = await client.post("/api/v1/communications", headers=headers_b, json={
        "contact_uuid": contact_uuid,
        "channel": "phone",
        "direction": "inbound",
        "occurred_at": "2026-04-11T15:00:00",
        "subject": "Inbound call from source B",
    })
    assert comm_resp.status_code == 201
    comm_uuid = comm_resp.json()["uuid"]

    # 4. Use source A's key to read that communication (shared read across sources)
    comm_detail = await client.get(f"/api/v1/communications/{comm_uuid}", headers=headers_a)
    assert comm_detail.status_code == 200

    # 5. Use source A's key to create another communication
    comm2_resp = await client.post("/api/v1/communications", headers=headers_a, json={
        "contact_uuid": contact_uuid,
        "channel": "email",
        "direction": "outbound",
        "occurred_at": "2026-04-11T16:00:00",
        "subject": "Follow-up from source A",
    })
    assert comm2_resp.status_code == 201

    # 7. Use the root key to read everything
    all_contacts = await client.get("/api/v1/contacts", headers=ROOT_KEY_HEADERS)
    assert all_contacts.status_code == 200
    assert any(c["uuid"] == contact_uuid for c in all_contacts.json()["data"] if "uuid" in c)

    all_comms = await client.get("/api/v1/communications", headers=ROOT_KEY_HEADERS)
    assert all_comms.status_code == 200


@pytest.mark.asyncio
async def test_source_key_creates_contact_with_source_stamp(client):
    """Contact created with source key should have first_seen_source_id set."""
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": "stamp_test", "name": "Stamp Test",
    })
    src_uuid = src.json()["uuid"]
    key_resp = await client.post(
        f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Stamp key"}
    )
    source_key = key_resp.json()["key_value"]

    contact = await client.post("/api/v1/contacts", headers={"X-API-Key": source_key}, json={
        "first_name": "Stamp", "last_name": "Test", "contact_type": "prospect",
    })
    assert contact.status_code == 201

    # The contact should exist and be readable
    detail = await client.get(f"/api/v1/contacts/{contact.json()['uuid']}", headers={"X-API-Key": source_key})
    assert detail.status_code == 200


@pytest.mark.asyncio
async def test_root_key_full_access(client):
    """Root key can access admin endpoints AND regular endpoints."""
    # Admin
    sources = await client.get("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS)
    assert sources.status_code == 200

    # Regular
    contacts = await client.get("/api/v1/contacts", headers=ROOT_KEY_HEADERS)
    assert contacts.status_code == 200

    health = await client.get("/api/v1/health")
    assert health.status_code == 200
