"""Tests for marketing-source derivation + the public listing endpoint.

Covers:
  - derive_codes() across UTM + referrer + empty signal cases
  - Contact create attaches derived codes when payload has none
  - Contact create honors explicit marketing_sources (no derivation)
  - GET /api/v1/marketing-sources public read
"""

import pytest

from app.services.marketing_source_service import derive_codes


# =============================================================================
# Pure derivation logic
# =============================================================================
@pytest.mark.parametrize(
    "refs,expected",
    [
        # No signal at all → website (conservative default)
        (None, ["website"]),
        ({}, ["website"]),
        ({"referrer": ""}, ["website"]),
        # UTM paid search
        ({"extra": {"utm_source": "google", "utm_medium": "cpc"}}, ["google_search"]),
        ({"extra": {"utm_source": "bing", "utm_medium": "ppc"}},   ["google_search"]),
        # UTM paid social
        ({"extra": {"utm_source": "facebook", "utm_medium": "cpc"}},   ["social_media_ad"]),
        ({"extra": {"utm_source": "instagram", "utm_medium": "paid"}}, ["social_media_ad"]),
        # UTM organic social (medium=social, no paid)
        ({"extra": {"utm_source": "facebook", "utm_medium": "social"}}, ["social_media_organic"]),
        # UTM organic search (just utm_source)
        ({"extra": {"utm_source": "google"}}, ["google_search"]),
        # UTM email
        ({"extra": {"utm_source": "newsletter", "utm_medium": "email"}}, ["other"]),
        # Referrer = google search
        ({"referrer": "https://www.google.com/search?q=dental+columbia"}, ["google_search"]),
        ({"referrer": "https://duckduckgo.com/?q=embroidery"},           ["google_search"]),
        # Referrer = social
        ({"referrer": "https://www.facebook.com/somepage"},   ["social_media_organic"]),
        ({"referrer": "https://x.com/someone"},                ["social_media_organic"]),
        # Referrer = same-domain or any other host (the on-site nav case)
        ({"referrer": "https://completedentalcarecolumbia.com/services/crowns"}, ["website"]),
        ({"referrer": "https://cleverorchid.com/book"},                          ["website"]),
        # Garbage referrer (non-URL string)
        ({"referrer": "not-a-url"}, ["website"]),
    ],
)
def test_derive_codes(refs, expected):
    assert derive_codes(refs) == expected


# =============================================================================
# End-to-end through POST /contacts
# =============================================================================
@pytest.mark.asyncio
async def test_create_contact_derives_marketing_source_from_referrer(
    client, auth_headers
):
    """Consumer site sends only referrer (the current CDC + CO behavior).

    The API must populate contact_marketing_sources with the derived
    'website' code (same-domain referrer is the SEO/on-site-nav case).
    """
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "DerivedFromRef",
            "last_name": "Tester",
            "contact_type": "lead",
            "external_refs_json": {
                "referrer": "https://completedentalcarecolumbia.com/services",
                "ip_address": "8.8.8.8",
            },
        },
    )
    assert resp.status_code == 201, resp.text
    uuid = resp.json()["uuid"]

    detail = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert "Website" in detail.json()["marketing_sources"]


@pytest.mark.asyncio
async def test_create_contact_derives_google_search_from_utm(client, auth_headers):
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "DerivedFromUtm",
            "last_name": "Tester",
            "contact_type": "lead",
            "external_refs_json": {
                "extra": {"utm_source": "google", "utm_medium": "cpc"},
                "ip_address": "8.8.8.8",
            },
        },
    )
    assert resp.status_code == 201, resp.text
    uuid = resp.json()["uuid"]

    detail = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert "Google Search" in detail.json()["marketing_sources"]


@pytest.mark.asyncio
async def test_create_contact_explicit_marketing_sources_wins(client, auth_headers):
    """Explicit list always wins over derivation, even when both present."""
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Explicit",
            "last_name": "Tester",
            "contact_type": "lead",
            "marketing_sources": ["referral"],  # explicit
            "external_refs_json": {
                # Would derive google_search if explicit were empty
                "extra": {"utm_source": "google", "utm_medium": "cpc"},
                "ip_address": "8.8.8.8",
            },
        },
    )
    assert resp.status_code == 201, resp.text
    uuid = resp.json()["uuid"]

    detail = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    sources = detail.json()["marketing_sources"]
    assert "Referral" in sources
    assert "Google Search" not in sources


@pytest.mark.asyncio
async def test_create_contact_no_external_refs_defaults_to_website(
    client, auth_headers
):
    """Zero signal → derive 'website' (conservative default)."""
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "NoSignal",
            "last_name": "Tester",
            "contact_type": "lead",
        },
    )
    assert resp.status_code == 201, resp.text
    uuid = resp.json()["uuid"]

    detail = await client.get(f"/api/v1/contacts/{uuid}", headers=auth_headers)
    assert "Website" in detail.json()["marketing_sources"]


# =============================================================================
# GET /api/v1/marketing-sources — public source-key gated
# =============================================================================
@pytest.mark.asyncio
async def test_get_marketing_sources_requires_auth(client):
    resp = await client.get("/api/v1/marketing-sources")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_marketing_sources_returns_seeded_codes(client, auth_headers):
    resp = await client.get("/api/v1/marketing-sources", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "data" in data
    codes = [row["code"] for row in data["data"]]
    # Migration 011 seeds these — assertion list is intentionally a subset
    # so a future seed addition doesn't break this test.
    for required in ("google_search", "social_media_ad", "social_media_organic",
                     "referral", "walk_in", "website", "other"):
        assert required in codes
    # Each row carries a human label
    for row in data["data"]:
        assert isinstance(row.get("label"), str) and row["label"]
