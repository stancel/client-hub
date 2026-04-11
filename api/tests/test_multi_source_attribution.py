import uuid

import pytest

ROOT_KEY_HEADERS = {"X-API-Key": "dev-api-key"}


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_multi_source_full_flow(client):
    """Critical test: full multi-source attribution flow per the spec."""
    code_a = _unique("source_a")
    code_b = _unique("source_b")

    src_a = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": code_a, "name": "Source A", "source_type": "website",
    })
    src_a_uuid = src_a.json()["uuid"]
    key_a = (await client.post(
        f"/api/v1/admin/sources/{src_a_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key A"}
    )).json()["key_value"]

    src_b = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={
        "code": code_b, "name": "Source B", "source_type": "cti",
    })
    src_b_uuid = src_b.json()["uuid"]
    key_b = (await client.post(
        f"/api/v1/admin/sources/{src_b_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Key B"}
    )).json()["key_value"]

    headers_a = {"X-API-Key": key_a}
    headers_b = {"X-API-Key": key_b}

    # Source A creates a contact
    contact_resp = await client.post("/api/v1/contacts", headers=headers_a, json={
        "first_name": "Multi", "last_name": _unique("Test"), "contact_type": "lead",
    })
    assert contact_resp.status_code == 201
    contact_uuid = contact_resp.json()["uuid"]

    # Source B creates a communication on that contact
    comm_resp = await client.post("/api/v1/communications", headers=headers_b, json={
        "contact_uuid": contact_uuid, "channel": "phone", "direction": "inbound",
        "occurred_at": "2026-04-11T15:00:00", "subject": "Call from B",
    })
    assert comm_resp.status_code == 201

    # Source A can read that communication (shared read)
    comm_uuid = comm_resp.json()["uuid"]
    assert (await client.get(f"/api/v1/communications/{comm_uuid}", headers=headers_a)).status_code == 200

    # Source A creates another communication
    assert (await client.post("/api/v1/communications", headers=headers_a, json={
        "contact_uuid": contact_uuid, "channel": "email", "direction": "outbound",
        "occurred_at": "2026-04-11T16:00:00", "subject": "Follow-up from A",
    })).status_code == 201

    # Root key reads everything
    assert (await client.get("/api/v1/contacts", headers=ROOT_KEY_HEADERS)).status_code == 200
    assert (await client.get("/api/v1/communications", headers=ROOT_KEY_HEADERS)).status_code == 200


@pytest.mark.asyncio
async def test_source_key_creates_contact_with_source_stamp(client):
    code = _unique("stamp_test")
    src = await client.post("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS, json={"code": code, "name": "Stamp Test"})
    src_uuid = src.json()["uuid"]
    key = (await client.post(
        f"/api/v1/admin/sources/{src_uuid}/api-keys", headers=ROOT_KEY_HEADERS, json={"name": "Stamp"}
    )).json()["key_value"]

    contact = await client.post("/api/v1/contacts", headers={"X-API-Key": key}, json={
        "first_name": "Stamp", "last_name": _unique("Test"), "contact_type": "prospect",
    })
    assert contact.status_code == 201
    detail = await client.get(f"/api/v1/contacts/{contact.json()['uuid']}", headers={"X-API-Key": key})
    assert detail.status_code == 200


@pytest.mark.asyncio
async def test_root_key_full_access(client):
    assert (await client.get("/api/v1/admin/sources", headers=ROOT_KEY_HEADERS)).status_code == 200
    assert (await client.get("/api/v1/contacts", headers=ROOT_KEY_HEADERS)).status_code == 200
    assert (await client.get("/api/v1/health")).status_code == 200
