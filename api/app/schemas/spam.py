from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

PatternKind = Literal[
    "email_substring",
    "full_email_block",
    "url_regex",
    "phrase_regex",
    "phone_country_block",
]

IntegrationKind = Literal["web_form", "webhook", "mcp", "direct_api", "other"]

RejectionReason = Literal[
    "phone_invalid",
    "email_blocked",
    "url_blocked",
    "phrase_combo",
    "rate_limit",
    "honeypot",
]


# =============================================================================
# Spam patterns
# =============================================================================
class SpamPatternPublic(BaseModel):
    """Slim shape returned to consumer sites (source-key gated)."""

    pattern_kind: PatternKind
    pattern: str

    model_config = {"from_attributes": True}


class SpamPatternsByKind(BaseModel):
    """Public response — patterns grouped by kind for easy consumer parsing."""

    email_substring: list[str]
    full_email_block: list[str]
    url_regex: list[str]
    phrase_regex: list[str]
    phone_country_block: list[str]


class SpamPatternOut(BaseModel):
    """Full admin shape — includes metadata."""

    uuid: str
    pattern_kind: PatternKind
    pattern: str
    notes: str | None = None
    is_active: bool
    hit_count: int
    last_hit_at: datetime | None = None
    false_positive_count: int
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None

    model_config = {"from_attributes": True}


class SpamPatternListResponse(BaseModel):
    data: list[SpamPatternOut]
    pagination: dict


class SpamPatternCreate(BaseModel):
    pattern_kind: PatternKind
    pattern: str
    notes: str | None = None
    is_active: bool = True


class SpamPatternUpdate(BaseModel):
    pattern: str | None = None
    notes: str | None = None
    is_active: bool | None = None


# =============================================================================
# Spam events
# =============================================================================
class SpamEventOut(BaseModel):
    uuid: str
    source_uuid: str | None = None
    endpoint: str
    integration_kind: IntegrationKind
    remote_ip: str | None = None
    submitted_email: str | None = None
    submitted_phone: str | None = None
    submitted_body_hash: str | None = None
    matched_pattern_uuid: str | None = None
    matched_pattern_text: str | None = None
    rejection_reason: RejectionReason
    payload_json: dict[str, Any] | None = None
    was_false_positive: bool
    occurred_at: datetime


class SpamEventListResponse(BaseModel):
    data: list[SpamEventOut]
    pagination: dict


# =============================================================================
# Spam-event analytics
# =============================================================================
class HitsByEndpoint(BaseModel):
    endpoint: str
    hits: int


class HitsByPattern(BaseModel):
    pattern_uuid: str | None = None
    pattern_kind: PatternKind | None = None
    pattern_text: str
    hits: int
    false_positives: int
    false_positive_rate: float


class HitsByIp(BaseModel):
    remote_ip: str
    hits: int


class SpamEventStats(BaseModel):
    total_events: int
    total_false_positives: int
    by_endpoint: list[HitsByEndpoint]
    by_pattern: list[HitsByPattern]
    by_ip_top: list[HitsByIp]
