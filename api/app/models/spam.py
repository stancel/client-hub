from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.lookups import Base


class SpamPattern(Base):
    __tablename__ = "spam_patterns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    pattern_kind: Mapped[str] = mapped_column(
        Enum(
            "email_substring",
            "full_email_block",
            "url_regex",
            "phrase_regex",
            "phone_country_block",
        ),
        nullable=False,
    )
    pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    last_hit_at: Mapped[datetime | None] = mapped_column(DateTime)
    false_positive_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    created_by: Mapped[str | None] = mapped_column(String(100))


class SpamEvent(Base):
    __tablename__ = "spam_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL")
    )
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    integration_kind: Mapped[str] = mapped_column(
        Enum("web_form", "webhook", "mcp", "direct_api", "other"),
        default="other",
        nullable=False,
    )
    remote_ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    submitted_email: Mapped[str | None] = mapped_column(String(255))
    submitted_phone: Mapped[str | None] = mapped_column(String(20))
    submitted_body_hash: Mapped[str | None] = mapped_column(String(16))
    matched_pattern_id: Mapped[int | None] = mapped_column(
        ForeignKey("spam_patterns.id", ondelete="SET NULL")
    )
    matched_pattern_text: Mapped[str | None] = mapped_column(String(500))
    rejection_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict | None] = mapped_column(JSON)
    was_false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    matched_pattern: Mapped["SpamPattern | None"] = relationship(
        foreign_keys=[matched_pattern_id]
    )


# spam_rate_log is intentionally NOT mapped as an ORM model — it's
# operational data accessed via raw SQL for performance, the schema
# is composite-key-only with no rich relationships, and ORM overhead
# would make the rate-limit hot path slower for no benefit.
