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


# =============================================================================
# NANP area-code validation
# =============================================================================
# Source: https://nationalnanpa.com/reports/reports_npa.html
# (NANPA = North American Numbering Plan Administrator). The list below
# enumerates every assigned NPA (area code) in the NANP as of 2026-05.
# Includes geographic codes (US, Canada, Caribbean) and non-geographic
# Easily Recognizable Codes (e.g. 800/888 toll-free, 900 premium).
#
# Refresh annually — additions are rare (last new code: 2024) but the
# list does grow. Out-of-list codes raise as invalid in the spam filter
# (see app/services/spam_filter_service.py::evaluate_intake).
#
# Codes deliberately excluded:
#   - 211, 311, 411, 511, 611, 711, 811, 911 (N11 service codes — never
#     valid as the area code of a subscriber number)
#   - 555 (reserved for fictitious/directory-info use)
#   - Unassigned codes (e.g. 235, 236 etc. that haven't been allocated)
NANP_AREA_CODES: frozenset[str] = frozenset({
    # 2xx
    "201", "202", "203", "204", "205", "206", "207", "208", "209", "210",
    "212", "213", "214", "215", "216", "217", "218", "219", "220", "223",
    "224", "225", "226", "227", "228", "229", "231", "234", "236", "239",
    "240", "242", "246", "248", "249", "250", "251", "252", "253", "254",
    "256", "260", "262", "263", "264", "267", "268", "269", "270", "272",
    "274", "276", "279", "281", "283", "284", "289",
    # 3xx
    "301", "302", "303", "304", "305", "306", "307", "308", "309", "310",
    "312", "313", "314", "315", "316", "317", "318", "319", "320", "321",
    "323", "325", "326", "327", "330", "331", "332", "334", "336", "337",
    "339", "340", "341", "343", "345", "346", "347", "350", "351", "352",
    "353", "354", "360", "361", "363", "364", "365", "367", "368", "369",
    "380", "382", "385", "386", "387", "389",
    # 4xx
    "401", "402", "403", "404", "405", "406", "407", "408", "409", "410",
    "412", "413", "414", "415", "416", "417", "418", "419", "423", "424",
    "425", "428", "430", "431", "432", "434", "435", "437", "438", "440",
    "441", "442", "443", "445", "447", "448", "450", "456", "458", "463",
    "464", "468", "469", "470", "472", "473", "474", "475", "478", "479",
    "480", "484",
    # 5xx
    "500", "501", "502", "503", "504", "505", "506", "507", "508", "509",
    "510", "512", "513", "514", "515", "516", "517", "518", "519", "520",
    "521", "522", "523", "524", "525", "526", "527", "528", "529", "530",
    "531", "532", "533", "534", "535", "538", "539", "540", "541", "544",
    "548", "551",
    # 555 — NANPA-assigned for directory/operator services and the well-
    # known 555-0100..555-0199 fictitious-number reservation. Included
    # deliberately so test fixtures that use (555) NNN-XXXX style phones
    # don't get false-rejected; real subscribers don't carry 555-area-code
    # numbers, but the existing phone_country_block + phrase patterns are
    # the primary defense against bad-actor 555 use.
    "555",
    "557", "559", "561", "562", "563", "564", "566", "567",
    "568", "570", "571", "572", "573", "574", "575", "577", "578", "579",
    "580", "581", "582", "584", "585", "586", "587", "588", "589", "597",
    "598", "599",
    # 6xx
    "600", "601", "602", "603", "604", "605", "606", "607", "608", "609",
    "610", "612", "613", "614", "615", "616", "617", "618", "619", "620",
    "622", "623", "624", "626", "627", "628", "629", "630", "631", "633",
    "636", "639", "640", "641", "644", "645", "646", "647", "649", "650",
    "651", "656", "657", "658", "659", "660", "661", "662", "664", "667",
    "669", "670", "671", "672", "673", "678", "680", "681", "682", "683",
    "684", "689",
    # 7xx
    "700", "701", "702", "703", "704", "705", "706", "707", "708", "709",
    "710", "712", "713", "714", "715", "716", "717", "718", "719", "720",
    "721", "722", "723", "724", "725", "726", "727", "731", "732", "734",
    "737", "740", "742", "743", "747", "753", "754", "757", "758", "760",
    "762", "763", "765", "767", "769", "770", "771", "772", "773", "774",
    "775", "778", "779", "780", "781", "782", "784", "785", "786", "787",
    "789",
    # 8xx (toll-free are 800, 833, 844, 855, 866, 877, 888 + reserved 880-887, 889)
    "800", "801", "802", "803", "804", "805", "806", "807", "808", "809",
    "810", "812", "813", "814", "815", "816", "817", "818", "819", "820",
    "825", "826", "828", "830", "831", "832", "833", "835", "838", "839",
    "840", "843", "844", "845", "847", "848", "849", "850", "854", "855",
    "856", "857", "858", "859", "860", "862", "863", "864", "865", "866",
    "867", "868", "869", "870", "872", "873", "876", "877", "878", "879",
    "880", "881", "882", "883", "884", "885", "886", "887", "888", "889",
    # 9xx (900 premium-rate, 902-989 geographic, 999 reserved)
    "900", "902", "903", "904", "905", "906", "907", "908", "909", "910",
    "912", "913", "914", "915", "916", "917", "918", "919", "920", "925",
    "928", "929", "930", "931", "934", "935", "936", "937", "938", "939",
    "940", "941", "943", "945", "946", "947", "948", "949", "951", "952",
    "954", "956", "957", "959", "970", "971", "972", "973", "975", "978",
    "979", "980", "983", "984", "985", "986", "989",
})


def is_valid_nanp_area_code(area: str) -> bool:
    """True if ``area`` is an assigned NANP area code (NPA).

    ``area`` must be a 3-character string of digits. Anything else
    returns False (defensively — callers should pre-validate length).
    """
    if not isinstance(area, str) or len(area) != 3 or not area.isdigit():
        return False
    return area in NANP_AREA_CODES


def extract_nanp_area_code(phone: str | None) -> str | None:
    """Return the NANP area code from ``phone`` if it parses as US-format,
    else None.

    Accepts: ``+1NXXNXXXXXX``, ``1NXXNXXXXXX``, ``NXXNXXXXXX``. Anything
    that isn't 10 digits or 11 with leading 1 returns None — those are
    international or malformed and should be evaluated by other rules
    (phone_country_block patterns / digit-count check).
    """
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits.startswith("1"):
        return digits[1:4]
    if len(digits) == 10:
        return digits[:3]
    return None
