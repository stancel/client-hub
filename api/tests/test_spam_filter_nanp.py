"""Tests for NANP area-code validation in the spam filter.

Driven by the v0.3.6 CDC breakthrough where ``+12356895054`` (area code
235 — not assigned in NANP) passed the digit-count check and the
``+235`` country-block substring (``+1...`` prefix breaks that match).
The new ``phone_invalid_areacode`` rule rejects bad area codes outright.
"""

import pymysql
import pytest

from app.config import settings
from app.services.phone_utils import (
    extract_nanp_area_code,
    is_valid_nanp_area_code,
)


def _query(sql: str, params: tuple | None = None):
    conn = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()


# =============================================================================
# Unit tests — helpers
# =============================================================================
@pytest.mark.parametrize(
    "phone,expected",
    [
        ("+18035551212", "803"),
        ("+12125551234", "212"),
        ("+12356895054", "235"),  # the breakthrough case
        ("18035551212", "803"),
        ("8035551212", "803"),
        ("(803) 555-1212", "803"),
        ("+447911123456", None),  # international
        ("+91987654321", None),
        ("garbage", None),
        ("", None),
        (None, None),
    ],
)
def test_extract_nanp_area_code(phone, expected):
    assert extract_nanp_area_code(phone) == expected


@pytest.mark.parametrize(
    "area,expected",
    [
        ("803", True),    # SC
        ("212", True),    # NYC
        ("415", True),    # SF
        ("808", True),    # HI
        ("416", True),    # Toronto, CA
        ("647", True),    # Toronto overlay
        ("800", True),    # toll-free
        ("888", True),    # toll-free
        ("235", False),   # the breakthrough
        ("311", False),   # service code
        ("411", False),   # service code
        ("911", False),   # emergency
        ("210", True),    # SA, TX
        ("999", False),   # reserved
        ("000", False),   # not a real NPA
        ("12", False),    # wrong length
        ("8035", False),  # wrong length
        ("ab3", False),   # non-digit
    ],
)
def test_is_valid_nanp_area_code(area, expected):
    assert is_valid_nanp_area_code(area) is expected


# =============================================================================
# End-to-end — POST /api/v1/contacts with bogus area code rejects
# =============================================================================
@pytest.mark.asyncio
async def test_contact_post_rejects_invalid_nanp_area_code(client, auth_headers):
    """The exact phone from the v0.3.6 CDC breakthrough must now reject."""
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Davis",
            "last_name": "BrownTest",
            "contact_type": "lead",
            "emails": [
                {"address": "nanp-rejection-test@example.org",
                 "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "+12356895054", "type": "mobile",
                 "is_primary": True}
            ],
            "external_refs_json": {"ip_address": "8.8.4.4"},
        },
    )
    assert resp.status_code == 422, resp.text

    rows = _query(
        "SELECT rejection_reason, matched_pattern_text, remote_ip, peer_ip "
        "FROM spam_events "
        "WHERE submitted_phone='+12356895054' "
        "ORDER BY occurred_at DESC LIMIT 1"
    )
    assert rows, "expected spam_events row for invalid area code"
    reason, pattern_text, remote_ip, _peer_ip = rows[0]
    assert reason == "phone_invalid_areacode"
    assert pattern_text == "235"
    assert remote_ip == "8.8.4.4"


@pytest.mark.asyncio
async def test_contact_post_accepts_valid_nanp_area_code(client, auth_headers):
    """Sanity check — area code 803 (South Carolina) must still pass."""
    resp = await client.post(
        "/api/v1/contacts",
        headers=auth_headers,
        json={
            "first_name": "Real",
            "last_name": "Lead",
            "contact_type": "lead",
            "emails": [
                {"address": "nanp-valid-test@example.org",
                 "type": "personal", "is_primary": True}
            ],
            "phones": [
                {"number": "+18035551212", "type": "mobile",
                 "is_primary": True}
            ],
            "external_refs_json": {"ip_address": "8.8.4.5"},
        },
    )
    assert resp.status_code == 201, resp.text
