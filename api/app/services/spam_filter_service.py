"""Spam-defense framework — service layer.

See docs/Spam-Defense-Pattern.rst for the full design. Public surface:

- IntakePayload                       — normalized intake from any integration
- SpamVerdict                         — match result (or None on clean)
- spam_check_or_raise(...)            — one-line guard for any handler
- list_active_patterns_grouped(...)   — public source-key read
- list_patterns_admin(...)            — admin paginated list
- create_pattern(...) / update_pattern(...) / delete_pattern(...)
- list_spam_events(...)               — admin paginated rejection log
- spam_event_stats(...)               — admin analytics
- mark_false_positive(...)            — admin correction path
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid as uuid_mod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy import desc, func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.models.spam import SpamEvent, SpamPattern

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================
RATE_LIMIT_WINDOW_SECONDS = 600  # 10 minutes
RATE_LIMIT_PRUNE_AGE_SECONDS = 3600  # 1 hour
PHRASE_MATCHES_REQUIRED_FOR_REJECTION = 2


# =============================================================================
# Public dataclasses
# =============================================================================
@dataclass
class IntakePayload:
    """Normalized intake — every integration adapter produces one of these."""

    email: str | None
    phone: str | None
    body: str | None
    remote_ip: str | None = None


@dataclass
class SpamVerdict:
    """Returned by evaluate_intake when a payload is rejected."""

    rejection_reason: str
    matched_pattern_id: int | None
    matched_pattern_text: str | None


# =============================================================================
# Phone validation
# =============================================================================
def is_valid_us_phone(raw: str | None) -> bool:
    """Strip non-digits; accept exactly 10, or 11 digits starting with 1."""
    if not raw:
        return False
    digits = re.sub(r"\D", "", raw)
    return len(digits) == 10 or (len(digits) == 11 and digits.startswith("1"))


# =============================================================================
# Pattern evaluation (returns the FIRST match per kind to keep it deterministic)
# =============================================================================
async def _load_active_patterns(db: AsyncSession) -> list[SpamPattern]:
    stmt = select(SpamPattern).where(SpamPattern.is_active == True)  # noqa: E712
    return list((await db.execute(stmt)).scalars().all())


def _email_haystack(email: str) -> str:
    return email.lower()


def _evaluate_email(email: str | None, patterns: list[SpamPattern]) -> SpamPattern | None:
    if not email:
        return None
    h = _email_haystack(email)
    # full_email_block: exact match first (most specific)
    for p in patterns:
        if p.pattern_kind == "full_email_block" and p.pattern.lower() == h:
            return p
    # email_substring: substring of local-part or domain
    for p in patterns:
        if p.pattern_kind == "email_substring" and p.pattern.lower() in h:
            return p
    return None


def _evaluate_phone(phone: str | None, patterns: list[SpamPattern]) -> SpamPattern | None:
    if not phone:
        return None
    for p in patterns:
        if p.pattern_kind == "phone_country_block" and p.pattern in phone:
            return p
    return None


def _evaluate_body_url(body: str | None, patterns: list[SpamPattern]) -> SpamPattern | None:
    if not body:
        return None
    for p in patterns:
        if p.pattern_kind != "url_regex":
            continue
        try:
            if re.search(p.pattern, body, flags=re.IGNORECASE):
                return p
        except re.error:
            logger.warning(
                "Invalid url_regex pattern id=%s — skipping", p.id, exc_info=True
            )
    return None


def _evaluate_body_phrases(
    body: str | None, patterns: list[SpamPattern]
) -> list[SpamPattern]:
    """Return ALL matching phrase patterns (caller decides if count >= threshold)."""
    if not body:
        return []
    matches: list[SpamPattern] = []
    for p in patterns:
        if p.pattern_kind != "phrase_regex":
            continue
        try:
            if re.search(p.pattern, body, flags=re.IGNORECASE):
                matches.append(p)
        except re.error:
            logger.warning(
                "Invalid phrase_regex pattern id=%s — skipping", p.id, exc_info=True
            )
    return matches


# =============================================================================
# Rate-limit
# =============================================================================
def _body_hash(body: str | None) -> str | None:
    if not body:
        return None
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


async def _is_rate_limited(db: AsyncSession, intake: IntakePayload) -> bool:
    """Check if (email) or (email||body_hash) has been seen in the last 10 min."""
    if not intake.email:
        return False

    keys: list[tuple[str, str]] = [("email", intake.email.lower())]
    bh = _body_hash(intake.body)
    if bh:
        keys.append(("email_body_hash", f"{intake.email.lower()}|{bh}"))

    for key_type, key_value in keys:
        stmt = text(
            "SELECT 1 FROM spam_rate_log "
            "WHERE key_type = :kt AND key_value = :kv "
            "AND occurred_at > DATE_SUB(NOW(), INTERVAL :w SECOND) LIMIT 1"
        )
        result = await db.execute(
            stmt, {"kt": key_type, "kv": key_value, "w": RATE_LIMIT_WINDOW_SECONDS}
        )
        if result.first() is not None:
            return True
    return False


async def _record_rate_log(db: AsyncSession, intake: IntakePayload) -> None:
    """Stamp the rate-log so future submissions can see this happened.

    Also opportunistically prunes rows older than 1 hour to keep the table bounded.
    """
    if not intake.email:
        return

    rows: list[dict[str, Any]] = [
        {"kt": "email", "kv": intake.email.lower()}
    ]
    bh = _body_hash(intake.body)
    if bh:
        rows.append(
            {"kt": "email_body_hash", "kv": f"{intake.email.lower()}|{bh}"}
        )
    if intake.remote_ip:
        rows.append({"kt": "ip", "kv": intake.remote_ip})

    for r in rows:
        # INSERT IGNORE because PK is (key_type, key_value, occurred_at) — at sub-
        # second resolution distinct, but we ignore the rare collision anyway.
        await db.execute(
            text(
                "INSERT IGNORE INTO spam_rate_log (key_type, key_value, occurred_at) "
                "VALUES (:kt, :kv, NOW())"
            ),
            r,
        )

    # Opportunistic prune
    await db.execute(
        text(
            "DELETE FROM spam_rate_log "
            "WHERE occurred_at < DATE_SUB(NOW(), INTERVAL :w SECOND)"
        ),
        {"w": RATE_LIMIT_PRUNE_AGE_SECONDS},
    )


# =============================================================================
# Core evaluator
# =============================================================================
async def evaluate_intake(
    db: AsyncSession, intake: IntakePayload
) -> SpamVerdict | None:
    """Return a SpamVerdict on rejection, or None if clean."""

    # 1) Phone digit-count check (always-on — not a DB pattern)
    if intake.phone is not None and not is_valid_us_phone(intake.phone):
        return SpamVerdict(
            rejection_reason="phone_invalid",
            matched_pattern_id=None,
            matched_pattern_text=None,
        )

    patterns = await _load_active_patterns(db)

    # 2) Phone country-code block patterns
    if (m := _evaluate_phone(intake.phone, patterns)) is not None:
        return SpamVerdict(
            rejection_reason="phone_invalid",
            matched_pattern_id=m.id,
            matched_pattern_text=m.pattern,
        )

    # 3) Email patterns
    if (m := _evaluate_email(intake.email, patterns)) is not None:
        return SpamVerdict(
            rejection_reason="email_blocked",
            matched_pattern_id=m.id,
            matched_pattern_text=m.pattern,
        )

    # 4) Body URL patterns
    if (m := _evaluate_body_url(intake.body, patterns)) is not None:
        return SpamVerdict(
            rejection_reason="url_blocked",
            matched_pattern_id=m.id,
            matched_pattern_text=m.pattern,
        )

    # 5) Body phrase patterns — require ≥ N matches
    phrase_matches = _evaluate_body_phrases(intake.body, patterns)
    if len(phrase_matches) >= PHRASE_MATCHES_REQUIRED_FOR_REJECTION:
        first = phrase_matches[0]
        return SpamVerdict(
            rejection_reason="phrase_combo",
            matched_pattern_id=first.id,
            matched_pattern_text=first.pattern,
        )

    # 6) Rate-limit check (last — so phone/email/body match first for clearer signal)
    if await _is_rate_limited(db, intake):
        return SpamVerdict(
            rejection_reason="rate_limit",
            matched_pattern_id=None,
            matched_pattern_text=None,
        )

    return None


# =============================================================================
# Event recording
# =============================================================================
async def _record_spam_event(
    db: AsyncSession,
    *,
    intake: IntakePayload,
    verdict: SpamVerdict,
    source_id: int | None,
    endpoint: str,
    integration_kind: str,
    payload: dict[str, Any] | None,
) -> None:
    event = SpamEvent(
        uuid=str(uuid_mod.uuid4()),
        source_id=source_id,
        endpoint=endpoint,
        integration_kind=integration_kind,
        remote_ip=intake.remote_ip,
        submitted_email=intake.email,
        submitted_phone=intake.phone,
        submitted_body_hash=_body_hash(intake.body),
        matched_pattern_id=verdict.matched_pattern_id,
        matched_pattern_text=verdict.matched_pattern_text,
        rejection_reason=verdict.rejection_reason,
        payload_json=json.dumps(payload) if payload is not None else None,
    )
    db.add(event)

    # Bump pattern hit-count if a pattern caused this
    if verdict.matched_pattern_id is not None:
        await db.execute(
            update(SpamPattern)
            .where(SpamPattern.id == verdict.matched_pattern_id)
            .values(
                hit_count=SpamPattern.hit_count + 1,
                last_hit_at=datetime.now(timezone.utc),
            )
        )

    await db.commit()


# =============================================================================
# Public guard for handlers — one-liner to inherit the framework
# =============================================================================
async def spam_check_or_raise(
    db: AsyncSession,
    intake: IntakePayload,
    *,
    source_id: int | None,
    endpoint: str,
    integration_kind: str,
    payload: dict[str, Any] | None = None,
) -> None:
    """Evaluate intake; raise HTTPException(422) on spam, otherwise no-op.

    On a clean payload, also records the rate-log so future submissions can
    detect bursts. On rejection, records a spam_events row and bumps the
    matched pattern's hit_count.
    """
    verdict = await evaluate_intake(db, intake)
    if verdict is not None:
        await _record_spam_event(
            db,
            intake=intake,
            verdict=verdict,
            source_id=source_id,
            endpoint=endpoint,
            integration_kind=integration_kind,
            payload=payload,
        )
        # Generic rejection message — don't leak which rule fired
        raise HTTPException(
            status_code=422,
            detail="Submission rejected. Please try again or contact us by phone.",
        )

    # Clean — record rate-log
    await _record_rate_log(db, intake)
    await db.commit()


# =============================================================================
# Pattern management — public source-key read
# =============================================================================
async def list_active_patterns_grouped(db: AsyncSession) -> dict[str, list[str]]:
    """Public read for consumer-site sync. Returns grouped-by-kind."""
    stmt = (
        select(SpamPattern.pattern_kind, SpamPattern.pattern)
        .where(SpamPattern.is_active == True)  # noqa: E712
        .order_by(SpamPattern.pattern_kind, SpamPattern.id)
    )
    rows = (await db.execute(stmt)).all()
    grouped: dict[str, list[str]] = {
        "email_substring": [],
        "full_email_block": [],
        "url_regex": [],
        "phrase_regex": [],
        "phone_country_block": [],
    }
    for kind, pattern in rows:
        grouped[kind].append(pattern)
    return grouped


# =============================================================================
# Pattern management — admin
# =============================================================================
async def list_patterns_admin(
    db: AsyncSession,
    *,
    page: int = 1,
    per_page: int = 50,
    is_active: bool | None = None,
    pattern_kind: str | None = None,
) -> dict[str, Any]:
    stmt = select(SpamPattern)
    if is_active is not None:
        stmt = stmt.where(SpamPattern.is_active == is_active)
    if pattern_kind is not None:
        stmt = stmt.where(SpamPattern.pattern_kind == pattern_kind)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        stmt.order_by(SpamPattern.pattern_kind, SpamPattern.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    rows = (await db.execute(stmt)).scalars().all()

    return {
        "data": [_serialize_pattern(p) for p in rows],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if per_page else 0,
        },
    }


async def get_pattern_by_uuid(
    db: AsyncSession, pattern_uuid: str
) -> SpamPattern | None:
    stmt = select(SpamPattern).where(SpamPattern.uuid == pattern_uuid)
    return (await db.execute(stmt)).scalar_one_or_none()


async def create_pattern(db: AsyncSession, data: dict[str, Any]) -> SpamPattern:
    if data.get("pattern_kind") in {"url_regex", "phrase_regex"}:
        try:
            re.compile(data["pattern"])
        except re.error as e:
            raise ValueError(f"Invalid regex: {e}") from e

    pattern = SpamPattern(
        uuid=str(uuid_mod.uuid4()),
        pattern_kind=data["pattern_kind"],
        pattern=data["pattern"],
        notes=data.get("notes"),
        is_active=data.get("is_active", True),
        created_by=data.get("created_by", "admin_api"),
    )
    db.add(pattern)
    await db.commit()
    await db.refresh(pattern)
    return pattern


async def update_pattern(
    db: AsyncSession, pattern: SpamPattern, data: dict[str, Any]
) -> SpamPattern:
    new_pattern_text = data.get("pattern")
    if new_pattern_text is not None and pattern.pattern_kind in {
        "url_regex",
        "phrase_regex",
    }:
        try:
            re.compile(new_pattern_text)
        except re.error as e:
            raise ValueError(f"Invalid regex: {e}") from e

    for field in ("pattern", "notes", "is_active"):
        if field in data and data[field] is not None:
            setattr(pattern, field, data[field])

    await db.commit()
    await db.refresh(pattern)
    return pattern


async def delete_pattern(db: AsyncSession, pattern: SpamPattern) -> None:
    await db.delete(pattern)
    await db.commit()


def _serialize_pattern(p: SpamPattern) -> dict[str, Any]:
    return {
        "uuid": p.uuid,
        "pattern_kind": p.pattern_kind,
        "pattern": p.pattern,
        "notes": p.notes,
        "is_active": bool(p.is_active),
        "hit_count": p.hit_count,
        "last_hit_at": p.last_hit_at.isoformat() if p.last_hit_at else None,
        "false_positive_count": p.false_positive_count,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        "created_by": p.created_by,
    }


# =============================================================================
# Spam events — admin list / stats / mark-false-positive
# =============================================================================
async def list_spam_events(
    db: AsyncSession,
    *,
    page: int = 1,
    per_page: int = 50,
    endpoint: str | None = None,
    integration_kind: str | None = None,
    rejection_reason: str | None = None,
    submitted_email: str | None = None,
    was_false_positive: bool | None = None,
) -> dict[str, Any]:
    stmt = select(SpamEvent, Source.uuid.label("source_uuid"), SpamPattern.uuid.label("pattern_uuid")).outerjoin(
        Source, SpamEvent.source_id == Source.id
    ).outerjoin(SpamPattern, SpamEvent.matched_pattern_id == SpamPattern.id)

    if endpoint is not None:
        stmt = stmt.where(SpamEvent.endpoint == endpoint)
    if integration_kind is not None:
        stmt = stmt.where(SpamEvent.integration_kind == integration_kind)
    if rejection_reason is not None:
        stmt = stmt.where(SpamEvent.rejection_reason == rejection_reason)
    if submitted_email is not None:
        stmt = stmt.where(SpamEvent.submitted_email == submitted_email)
    if was_false_positive is not None:
        stmt = stmt.where(SpamEvent.was_false_positive == was_false_positive)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        stmt.order_by(desc(SpamEvent.occurred_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    rows = (await db.execute(stmt)).all()

    return {
        "data": [_serialize_event(ev, source_uuid, pattern_uuid) for ev, source_uuid, pattern_uuid in rows],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if per_page else 0,
        },
    }


def _serialize_event(
    ev: SpamEvent, source_uuid: str | None, pattern_uuid: str | None
) -> dict[str, Any]:
    payload: dict[str, Any] | None = None
    if ev.payload_json:
        try:
            payload = (
                ev.payload_json if isinstance(ev.payload_json, dict)
                else json.loads(ev.payload_json)
            )
        except (TypeError, ValueError):
            payload = None
    return {
        "uuid": ev.uuid,
        "source_uuid": source_uuid,
        "endpoint": ev.endpoint,
        "integration_kind": ev.integration_kind,
        "remote_ip": ev.remote_ip,
        "submitted_email": ev.submitted_email,
        "submitted_phone": ev.submitted_phone,
        "submitted_body_hash": ev.submitted_body_hash,
        "matched_pattern_uuid": pattern_uuid,
        "matched_pattern_text": ev.matched_pattern_text,
        "rejection_reason": ev.rejection_reason,
        "payload_json": payload,
        "was_false_positive": bool(ev.was_false_positive),
        "occurred_at": ev.occurred_at.isoformat() if ev.occurred_at else None,
    }


async def spam_event_stats(db: AsyncSession) -> dict[str, Any]:
    total = (
        await db.execute(select(func.count()).select_from(SpamEvent))
    ).scalar() or 0
    total_fp = (
        await db.execute(
            select(func.count())
            .select_from(SpamEvent)
            .where(SpamEvent.was_false_positive == True)  # noqa: E712
        )
    ).scalar() or 0

    by_endpoint = (
        await db.execute(
            select(SpamEvent.endpoint, func.count().label("hits"))
            .group_by(SpamEvent.endpoint)
            .order_by(desc("hits"))
        )
    ).all()

    by_pattern = (
        await db.execute(
            select(
                SpamPattern.uuid,
                SpamPattern.pattern_kind,
                SpamPattern.pattern,
                SpamPattern.hit_count,
                SpamPattern.false_positive_count,
            )
            .where(SpamPattern.hit_count > 0)
            .order_by(desc(SpamPattern.hit_count))
            .limit(50)
        )
    ).all()

    by_ip = (
        await db.execute(
            select(SpamEvent.remote_ip, func.count().label("hits"))
            .where(SpamEvent.remote_ip.is_not(None))
            .group_by(SpamEvent.remote_ip)
            .order_by(desc("hits"))
            .limit(20)
        )
    ).all()

    return {
        "total_events": int(total),
        "total_false_positives": int(total_fp),
        "by_endpoint": [
            {"endpoint": row[0], "hits": int(row[1])} for row in by_endpoint
        ],
        "by_pattern": [
            {
                "pattern_uuid": row[0],
                "pattern_kind": row[1],
                "pattern_text": row[2],
                "hits": int(row[3]),
                "false_positives": int(row[4]),
                "false_positive_rate": (
                    round(row[4] / row[3], 4) if row[3] > 0 else 0.0
                ),
            }
            for row in by_pattern
        ],
        "by_ip_top": [
            {"remote_ip": row[0], "hits": int(row[1])} for row in by_ip
        ],
    }


async def get_event_by_uuid(
    db: AsyncSession, event_uuid: str
) -> SpamEvent | None:
    stmt = select(SpamEvent).where(SpamEvent.uuid == event_uuid)
    return (await db.execute(stmt)).scalar_one_or_none()


async def mark_false_positive(
    db: AsyncSession, event: SpamEvent
) -> SpamEvent:
    """Set was_false_positive=TRUE and bump the matched pattern's FP counter."""
    if event.was_false_positive:
        return event  # idempotent

    event.was_false_positive = True
    if event.matched_pattern_id is not None:
        await db.execute(
            update(SpamPattern)
            .where(SpamPattern.id == event.matched_pattern_id)
            .values(false_positive_count=SpamPattern.false_positive_count + 1)
        )
    await db.commit()
    await db.refresh(event)
    return event
