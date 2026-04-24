from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.lookups import Base


class SeniorityLevel(Base):
    __tablename__ = "seniority_levels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ContactOrgAffiliation(Base):
    __tablename__ = "contact_org_affiliations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    role_title: Mapped[str | None] = mapped_column(String(200))
    department: Mapped[str | None] = mapped_column(String(100))
    seniority_level_id: Mapped[int | None] = mapped_column(
        ForeignKey("seniority_levels.id", ondelete="SET NULL")
    )
    is_decision_maker: Mapped[bool] = mapped_column(Boolean, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    # is_primary_key is a DB-side VIRTUAL generated column used only to
    # back the ux_coa_one_primary UNIQUE index — intentionally unmapped.
    start_date: Mapped[datetime | None] = mapped_column(Date)
    end_date: Mapped[datetime | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes_text: Mapped[str | None] = mapped_column(Text)
    external_refs_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[str | None] = mapped_column(String(100))

    contact: Mapped["Contact"] = relationship(back_populates="affiliations")
    organization: Mapped["Organization"] = relationship(back_populates="affiliations")
    seniority_level: Mapped["SeniorityLevel | None"] = relationship(foreign_keys=[seniority_level_id])


from app.models.contact import Contact  # noqa: E402
from app.models.organization import Organization  # noqa: E402
