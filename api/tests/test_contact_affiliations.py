import pytest


async def _find_contact_with_affiliation(client, auth_headers):
    """Find a contact that has ≥1 affiliation (Dr. Michael Chen in seed data)."""
    resp = await client.get("/api/v1/contacts?search=Chen", headers=auth_headers)
    data = resp.json()
    assert data["pagination"]["total"] >= 1
    return data["data"][0]["uuid"]


async def _create_test_org(client, auth_headers, name="Test Affiliation Org"):
    resp = await client.post(
        "/api/v1/organizations",
        headers=auth_headers,
        json={"name": name, "org_type": "employer"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["uuid"]


async def _create_test_contact(client, auth_headers, first="Aff", last="Test"):
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={"first_name": first, "last_name": last, "contact_type": "lead"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["uuid"]


@pytest.mark.asyncio
async def test_list_affiliations_seed_contact(client, auth_headers):
    uuid = await _find_contact_with_affiliation(client, auth_headers)
    resp = await client.get(f"/api/v1/contacts/{uuid}/affiliations", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    aff = data["data"][0]
    assert aff["is_primary"] is True
    assert aff["is_active"] is True
    assert aff["organization"]["name"]  # seed: Dallas Dental Group


@pytest.mark.asyncio
async def test_list_affiliations_contact_not_found(client, auth_headers):
    resp = await client.get(
        "/api/v1/contacts/00000000-0000-0000-0000-000000000000/affiliations",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_affiliation_basic(client, auth_headers):
    contact_uuid = await _create_test_contact(client, auth_headers, first="CreateAff", last="Basic")
    org_uuid = await _create_test_org(client, auth_headers, name="Create Aff Basic Org")

    resp = await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={
            "organization_uuid": org_uuid,
            "role_title": "Director of Ops",
            "department": "Operations",
            "seniority": "senior",
            "is_decision_maker": True,
            "is_primary": True,
        },
    )
    assert resp.status_code == 201, resp.text
    aff = resp.json()
    assert aff["role_title"] == "Director of Ops"
    assert aff["department"] == "Operations"
    assert aff["seniority"] == "senior"
    assert aff["is_decision_maker"] is True
    assert aff["is_primary"] is True
    assert aff["organization"]["uuid"] == org_uuid


@pytest.mark.asyncio
async def test_create_affiliation_unknown_org(client, auth_headers):
    contact_uuid = await _create_test_contact(client, auth_headers, first="UnknownOrg", last="Aff")
    resp = await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": "00000000-0000-0000-0000-000000000000", "role_title": "X"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_affiliation_demotes_previous_primary(client, auth_headers):
    contact_uuid = await _create_test_contact(client, auth_headers, first="Demote", last="Primary")
    org_a = await _create_test_org(client, auth_headers, name="Demote Org A")
    org_b = await _create_test_org(client, auth_headers, name="Demote Org B")

    # First affiliation — primary
    resp_a = await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": org_a, "is_primary": True},
    )
    aff_a_uuid = resp_a.json()["uuid"]

    # Second affiliation — also primary; first should be demoted
    resp_b = await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": org_b, "is_primary": True},
    )
    assert resp_b.status_code == 201

    listing = (await client.get(
        f"/api/v1/contacts/{contact_uuid}/affiliations", headers=auth_headers
    )).json()
    primaries = [a for a in listing["data"] if a["is_primary"]]
    assert len(primaries) == 1, f"expected exactly one primary, got {len(primaries)}"
    assert primaries[0]["organization"]["uuid"] == org_b

    # aff_a should be present but not primary
    aff_a = next(a for a in listing["data"] if a["uuid"] == aff_a_uuid)
    assert aff_a["is_primary"] is False


@pytest.mark.asyncio
async def test_update_affiliation_promote_to_primary(client, auth_headers):
    contact_uuid = await _create_test_contact(client, auth_headers, first="Promote", last="Later")
    org_a = await _create_test_org(client, auth_headers, name="Promote Org A")
    org_b = await _create_test_org(client, auth_headers, name="Promote Org B")

    a = await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": org_a, "is_primary": True},
    )
    b = await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": org_b, "is_primary": False},
    )
    a_uuid = a.json()["uuid"]
    b_uuid = b.json()["uuid"]

    resp = await client.put(
        f"/api/v1/contacts/{contact_uuid}/affiliations/{b_uuid}",
        headers=auth_headers,
        json={"is_primary": True},
    )
    assert resp.status_code == 200
    assert resp.json()["is_primary"] is True

    listing = (await client.get(
        f"/api/v1/contacts/{contact_uuid}/affiliations", headers=auth_headers
    )).json()
    primaries = [x for x in listing["data"] if x["is_primary"]]
    assert len(primaries) == 1
    assert primaries[0]["uuid"] == b_uuid
    # a should still exist but no longer be primary
    a_row = next(x for x in listing["data"] if x["uuid"] == a_uuid)
    assert a_row["is_primary"] is False


@pytest.mark.asyncio
async def test_update_affiliation_close_out(client, auth_headers):
    contact_uuid = await _create_test_contact(client, auth_headers, first="Close", last="Out")
    org_uuid = await _create_test_org(client, auth_headers, name="Close Out Org")
    aff_uuid = (await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": org_uuid, "is_primary": True},
    )).json()["uuid"]

    resp = await client.put(
        f"/api/v1/contacts/{contact_uuid}/affiliations/{aff_uuid}",
        headers=auth_headers,
        json={"end_date": "2026-04-23", "is_active": False},
    )
    assert resp.status_code == 200
    row = resp.json()
    assert row["is_active"] is False
    assert row["end_date"] == "2026-04-23"


@pytest.mark.asyncio
async def test_delete_affiliation_promotes_replacement(client, auth_headers):
    contact_uuid = await _create_test_contact(client, auth_headers, first="DelPromote", last="Test")
    org_a = await _create_test_org(client, auth_headers, name="DelPromote Org A")
    org_b = await _create_test_org(client, auth_headers, name="DelPromote Org B")

    aff_a = (await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": org_a, "is_primary": True},
    )).json()
    aff_b = (await client.post(
        f"/api/v1/contacts/{contact_uuid}/affiliations",
        headers=auth_headers,
        json={"organization_uuid": org_b, "is_primary": False},
    )).json()

    # Delete the primary — b should be auto-promoted
    resp = await client.delete(
        f"/api/v1/contacts/{contact_uuid}/affiliations/{aff_a['uuid']}",
        headers=auth_headers,
    )
    assert resp.status_code == 204

    listing = (await client.get(
        f"/api/v1/contacts/{contact_uuid}/affiliations", headers=auth_headers
    )).json()
    assert listing["count"] == 1
    assert listing["data"][0]["uuid"] == aff_b["uuid"]
    assert listing["data"][0]["is_primary"] is True


@pytest.mark.asyncio
async def test_delete_affiliation_not_found(client, auth_headers):
    contact_uuid = await _create_test_contact(client, auth_headers, first="DelNotFound", last="Test")
    resp = await client.delete(
        f"/api/v1/contacts/{contact_uuid}/affiliations/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_contact_create_with_inline_affiliation(client, auth_headers):
    org_uuid = await _create_test_org(client, auth_headers, name="Inline Aff Org")
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Inline",
            "last_name": "Affiliated",
            "contact_type": "client",
            "affiliations": [
                {
                    "organization_uuid": org_uuid,
                    "role_title": "Partner",
                    "seniority": "exec",
                    "is_primary": True,
                }
            ],
        },
    )
    assert resp.status_code == 201
    contact_uuid = resp.json()["uuid"]

    get_resp = await client.get(f"/api/v1/contacts/{contact_uuid}", headers=auth_headers)
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["primary_organization_uuid"] == org_uuid
    assert data["primary_role_title"] == "Partner"
    assert len(data["affiliations"]) == 1
    assert data["affiliations"][0]["organization"]["uuid"] == org_uuid


@pytest.mark.asyncio
async def test_contact_summary_includes_primary_org(client, auth_headers):
    contact_uuid = await _find_contact_with_affiliation(client, auth_headers)
    resp = await client.get(f"/api/v1/contacts/{contact_uuid}/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "primary_organization_uuid" in data
    assert "primary_organization_name" in data
    assert "primary_role_title" in data
    assert "primary_department" in data
    # Seed contact Dr. Chen has an affiliation
    assert data["primary_organization_name"] is not None


@pytest.mark.asyncio
async def test_contact_detail_includes_affiliation_uuid_on_phone(client, auth_headers):
    """Phones with affiliation_id should surface the affiliation_uuid; NULL stays None."""
    uuid = await _find_contact_with_affiliation(client, auth_headers)
    resp = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert resp.status_code == 200
    phones = resp.json()["phones"]
    # Seed phones don't have affiliation_id set, so all should be None
    for p in phones:
        assert "affiliation_uuid" in p
        assert p["affiliation_uuid"] is None
