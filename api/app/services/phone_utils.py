"""Phone-number normalization → E.164.

E.164 is the ITU-T international telecom standard:
``+`` followed by the country code and the subscriber digits, max 15
digits total, no formatting characters. Examples: ``+15558675309`` (US),
``+447911123456`` (UK), ``+819012345678`` (JP).

The Client Hub stores all phone numbers in E.164 because the SIP/CTI
caller-lookup endpoint does literal string equality, and free-form
storage breaks lookup on the first formatting variant
(``(803) 555-1212`` vs ``8035551212`` vs ``+18035551212``). Display
formatting is a presentation concern; storage is normalized.

This module is the single point of normalization. The Pydantic schema
calls it on every contact ingest, the lookup endpoint normalizes its
path parameter the same way, and migration 027's backfill uses it
on every existing row. A CHECK constraint at the DB layer catches
any future direct-DB writer that bypasses the API.
"""

from __future__ import annotations

import re

E164_PATTERN = re.compile(r"^\+[0-9]{10,15}$")


class PhoneNormalizationError(ValueError):
    """Raised when a phone number cannot be normalized to E.164."""


def _strip_to_digits(raw: str) -> str:
    return re.sub(r"\D", "", raw or "")


def normalize_to_e164(raw: str | None, *, default_country: str = "US") -> str:
    """Convert ``raw`` to E.164 (``+CCNNNNNNNNNN``) or raise.

    Accepts the common US-customer inputs we see in the wild:

    - Already-E.164: ``+15558675309`` → returned as-is (after validation).
    - 10-digit US: ``8035551212`` / ``(803) 555-1212`` / ``803-555-1212``
      → ``+18035551212``.
    - 11-digit US with leading 1: ``18035551212`` / ``1 (803) 555-1212``
      → ``+18035551212``.
    - International with leading ``+``: digits-only validated against
      the 10–15 length window.

    Anything that can't be coerced to one of the above raises
    ``PhoneNormalizationError`` so the API caller gets a 422 with a
    pointed message rather than a silent bad write.

    ``default_country`` is included for future extensibility but only
    ``"US"`` is implemented today — that's all the consumer sites
    feed us, and the spam filter already rejects offshore traffic via
    seeded ``phone_country_block`` patterns.
    """
    if raw is None:
        raise PhoneNormalizationError("phone number is required")

    s = str(raw).strip()
    if not s:
        raise PhoneNormalizationError("phone number is empty")

    if s.startswith("+"):
        digits = _strip_to_digits(s[1:])
        if not (10 <= len(digits) <= 15):
            raise PhoneNormalizationError(
                f"E.164 phone must have 10-15 digits after '+'; got {len(digits)}: {raw!r}"
            )
        return f"+{digits}"

    digits = _strip_to_digits(s)
    if default_country == "US":
        if len(digits) == 10:
            return f"+1{digits}"
        if len(digits) == 11 and digits.startswith("1"):
            return f"+{digits}"
        raise PhoneNormalizationError(
            f"US phone must have 10 digits, or 11 starting with 1; got {len(digits)} digits: {raw!r}"
        )

    raise PhoneNormalizationError(
        f"unsupported default_country={default_country!r}; only 'US' is implemented"
    )


def is_e164(value: str | None) -> bool:
    """True if ``value`` matches ``^\\+[0-9]{10,15}$``. No coercion."""
    if not value:
        return False
    return bool(E164_PATTERN.match(value))
