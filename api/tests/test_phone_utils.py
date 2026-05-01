"""Tests for phone normalization to E.164."""

import pytest

from app.services.phone_utils import (
    PhoneNormalizationError,
    is_e164,
    normalize_to_e164,
)


# =============================================================================
# US 10-digit inputs (the common case)
# =============================================================================
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("8035551212",          "+18035551212"),
        ("803-555-1212",        "+18035551212"),
        ("(803) 555-1212",      "+18035551212"),
        ("803.555.1212",        "+18035551212"),
        ("803 555 1212",        "+18035551212"),
        ("  8035551212  ",      "+18035551212"),
        # The actual prod data we saw on CDC + CO
        ("8149805065",          "+18149805065"),
        ("803-665-9024",        "+18036659024"),
        ("(808) 256-8182",      "+18082568182"),
    ],
)
def test_normalize_us_10digit(raw, expected):
    assert normalize_to_e164(raw) == expected


# =============================================================================
# US 11-digit with leading 1
# =============================================================================
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("18035551212",         "+18035551212"),
        ("1-803-555-1212",      "+18035551212"),
        ("1 (803) 555-1212",    "+18035551212"),
    ],
)
def test_normalize_us_11digit_leading_1(raw, expected):
    assert normalize_to_e164(raw) == expected


# =============================================================================
# Already E.164
# =============================================================================
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("+18035551212",        "+18035551212"),
        ("+1 803 555 1212",     "+18035551212"),
        ("+447911123456",       "+447911123456"),  # UK
        ("+819012345678",       "+819012345678"),  # JP
    ],
)
def test_normalize_already_e164(raw, expected):
    assert normalize_to_e164(raw) == expected


# =============================================================================
# Rejections
# =============================================================================
@pytest.mark.parametrize(
    "bad",
    [
        None,
        "",
        "   ",
        "abc",
        "12345",                # too short
        "12345678901234567",    # too long
        "+12345",               # E.164 too short
        "+1234567890123456",    # E.164 too long
        "555-12345",            # 8 digits
        "+",                    # just plus
    ],
)
def test_normalize_rejects_garbage(bad):
    with pytest.raises(PhoneNormalizationError):
        normalize_to_e164(bad)


# =============================================================================
# is_e164 helper
# =============================================================================
def test_is_e164_true():
    for v in ("+18035551212", "+447911123456", "+819012345678"):
        assert is_e164(v) is True


def test_is_e164_false():
    for v in (None, "", "8035551212", "(803) 555-1212", "+", "+1234"):
        assert is_e164(v) is False
