"""Marketing-source attribution — derivation + lookup.

Every contact created through the API is attributed to one or more
``marketing_sources`` (Google search, social media, referral, walk-in,
etc.) via the ``contact_marketing_sources`` junction. Two paths feed
the junction:

1. **Explicit** — the consumer site sends ``marketing_sources: ["..."]``
   in the POST /contacts body. Used by sites that capture UTMs and
   ad-platform attribution server-side. Always wins.
2. **Derived** — when the explicit list is empty, ``derive_codes`` runs
   against ``external_refs_json`` (UTM params + referrer URL) and
   returns the best-effort code list. Used today by both consumer
   sites (CDC + Clever Orchid) which only capture referrer + URL but
   no UTMs (all current traffic is SEO/inbound).

The derivation is intentionally conservative: when no signal is
available, default to ``"website"`` rather than guessing. Display
labels and active state live in the ``marketing_sources`` lookup
table — see migration 011 for seeded codes.

Public read of the canonical code list is exposed via
``GET /api/v1/marketing-sources`` so consumer sites pull the list
rather than hardcoding it (same pattern as ``/spam-patterns``).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact, ContactMarketingSource
from app.models.lookups import MarketingSource

# =============================================================================
# Derivation
# =============================================================================
_SEARCH_HOSTS = ("google.", "bing.", "duckduckgo.", "yahoo.")
_SOCIAL_HOSTS = (
    "facebook.", "instagram.", "twitter.", "x.com",
    "linkedin.", "tiktok.", "pinterest.", "reddit.",
)
_PAID_MEDIUMS = {"cpc", "paid", "ppc", "display", "banner"}
_SOCIAL_MEDIUMS = {"social", "organic_social", "social-organic"}
_EMAIL_MEDIUMS = {"email", "newsletter"}
_PAID_SOCIAL_SOURCES = {
    "facebook", "instagram", "twitter", "x",
    "linkedin", "tiktok", "pinterest", "reddit",
}
_SEARCH_SOURCES = {"google", "bing", "duckduckgo", "yahoo"}


def _hostname(url: str) -> str:
    """Return the lowercased hostname of ``url`` or '' on failure."""
    try:
        host = urlparse(url).hostname
    except (TypeError, ValueError):
        return ""
    return (host or "").lower()


def derive_codes(external_refs_json: dict[str, Any] | None) -> list[str]:
    """Best-effort marketing-source codes from a contact's external refs.

    Precedence (most-specific first):

    1. Explicit UTM parameters in ``external_refs_json.extra.utm_*``.
    2. Document referrer hostname.
    3. Default to ``["website"]`` when no signal is available.

    Returns a list of *codes* (matching ``marketing_sources.code``);
    callers should resolve them to ids via ``attach_codes`` which
    silently drops codes that don't exist in the lookup table (a code
    rename in the seed data shouldn't error a contact create).
    """
    if not external_refs_json:
        return ["website"]

    extra = external_refs_json.get("extra") or {}
    utm_source = (extra.get("utm_source") or "").strip().lower()
    utm_medium = (extra.get("utm_medium") or "").strip().lower()

    # ---- Path 1: explicit UTM params ----
    if utm_source or utm_medium:
        if utm_medium in _PAID_MEDIUMS:
            if utm_source in _SEARCH_SOURCES:
                # Paid search — closest seeded code is google_search
                return ["google_search"]
            return ["social_media_ad"]
        if utm_medium in _SOCIAL_MEDIUMS:
            return ["social_media_organic"]
        if utm_medium in _EMAIL_MEDIUMS:
            # No canonical "email" code seeded yet — bucket as "other" so
            # the junction is populated and the gap is visible
            return ["other"]
        if utm_source in _SEARCH_SOURCES:
            return ["google_search"]
        if utm_source in _PAID_SOCIAL_SOURCES:
            return ["social_media_organic"]
        return ["other"]

    # ---- Path 2: referrer hostname ----
    referrer = (external_refs_json.get("referrer") or "").strip()
    host = _hostname(referrer)
    if host:
        if any(h in host for h in _SEARCH_HOSTS):
            return ["google_search"]
        if any(h in host for h in _SOCIAL_HOSTS):
            return ["social_media_organic"]
        # Same-domain referrer or any other host: the visitor was on the
        # consumer site when they submitted the form. Without first-touch
        # tracking we can't know how they arrived; "website" is the
        # honest answer.
        return ["website"]

    # ---- Path 3: no signal ----
    return ["website"]


# =============================================================================
# Persistence — apply codes to a contact
# =============================================================================
async def attach_codes(
    db: AsyncSession,
    contact: Contact,
    codes: list[str],
    *,
    source_detail: str | None = None,
) -> int:
    """Attach ``codes`` to ``contact`` via the junction. Returns count attached.

    Codes that don't resolve to an active row in ``marketing_sources``
    are silently skipped — a typo or renamed seed shouldn't break a
    contact create. Duplicates within ``codes`` are deduplicated.
    ``source_detail`` is a free-form note (e.g. ``"derived"`` to
    distinguish auto-attribution from explicit consumer-site values).
    """
    if not codes:
        return 0

    seen: set[str] = set()
    deduped: list[str] = []
    for c in codes:
        if c and c not in seen:
            seen.add(c)
            deduped.append(c)

    rows = (
        await db.execute(
            select(MarketingSource).where(MarketingSource.code.in_(deduped))
        )
    ).scalars().all()
    by_code = {r.code: r for r in rows}

    now = datetime.now(timezone.utc)
    attached = 0
    for code in deduped:
        ms = by_code.get(code)
        if ms is None:
            continue
        contact.marketing_sources.append(
            ContactMarketingSource(
                marketing_source_id=ms.id,
                source_detail=source_detail,
                attributed_at=now,
            )
        )
        attached += 1
    return attached


# =============================================================================
# Public read — used by consumer sites + the GET /marketing-sources endpoint
# =============================================================================
async def list_active_marketing_sources(db: AsyncSession) -> list[dict[str, Any]]:
    """Return active marketing-source codes + labels for consumer-site sync.

    Mirrors the ``/spam-patterns`` public-read pattern: source-key
    gated, returns canonical data, consumer sites pull this at build
    time rather than hardcoding the list.
    """
    stmt = (
        select(MarketingSource)
        .where(MarketingSource.is_active == True)  # noqa: E712
        .order_by(MarketingSource.id)
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [{"code": r.code, "label": r.label} for r in rows]
