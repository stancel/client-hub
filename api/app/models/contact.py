from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.lookups import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    contact_type_id: Mapped[int] = mapped_column(ForeignKey("contact_types.id"))
    first_seen_source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="RESTRICT"))
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    date_of_birth: Mapped[str | None] = mapped_column(String(10))
    converted_at: Mapped[datetime | None] = mapped_column(DateTime)
    converted_from_type_id: Mapped[int | None] = mapped_column(ForeignKey("contact_types.id"))
    enrichment_status: Mapped[str] = mapped_column(
        Enum("complete", "partial", "needs_review"), default="partial"
    )
    marketing_opt_out_sms: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_opt_out_email: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_opt_out_phone: Mapped[bool] = mapped_column(Boolean, default=False)
    notes_text: Mapped[str | None] = mapped_column(Text)
    external_refs_json: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[str | None] = mapped_column(String(100))

    contact_type: Mapped["ContactType"] = relationship(foreign_keys=[contact_type_id])
    converted_from_type: Mapped["ContactType | None"] = relationship(foreign_keys=[converted_from_type_id])
    first_seen_source: Mapped["Source"] = relationship(foreign_keys=[first_seen_source_id])
    organization: Mapped["Organization | None"] = relationship(back_populates="contacts")
    phones: Mapped[list["ContactPhone"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    emails: Mapped[list["ContactEmail"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    addresses: Mapped[list["ContactAddress"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    channel_prefs: Mapped[list["ContactChannelPref"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    marketing_sources: Mapped[list["ContactMarketingSource"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    tags: Mapped[list["ContactTagMap"]] = relationship(cascade="all, delete-orphan")
    notes: Mapped[list["ContactNote"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    preferences: Mapped[list["ContactPreference"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    orders: Mapped[list] = relationship("Order", back_populates="contact")
    communications: Mapped[list] = relationship("Communication", back_populates="contact")


class ContactPhone(Base):
    __tablename__ = "contact_phones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    phone_type_id: Mapped[int] = mapped_column(ForeignKey("phone_types.id"))
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_extension: Mapped[str | None] = mapped_column(String(10))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    data_source: Mapped[str | None] = mapped_column(String(50))
    is_enriched: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contact: Mapped["Contact"] = relationship(back_populates="phones")
    phone_type: Mapped["PhoneType"] = relationship()


class ContactEmail(Base):
    __tablename__ = "contact_emails"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    email_type_id: Mapped[int] = mapped_column(ForeignKey("email_types.id"))
    email_address: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    data_source: Mapped[str | None] = mapped_column(String(50))
    is_enriched: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contact: Mapped["Contact"] = relationship(back_populates="emails")
    email_type: Mapped["EmailType"] = relationship()


class ContactAddress(Base):
    __tablename__ = "contact_addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    address_type_id: Mapped[int] = mapped_column(ForeignKey("address_types.id"))
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="US")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    data_source: Mapped[str | None] = mapped_column(String(50))
    is_enriched: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contact: Mapped["Contact"] = relationship(back_populates="addresses")
    address_type: Mapped["AddressType"] = relationship()


class ContactChannelPref(Base):
    __tablename__ = "contact_channel_prefs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    channel_type_id: Mapped[int] = mapped_column(ForeignKey("channel_types.id"))
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    opt_in_status: Mapped[str] = mapped_column(
        Enum("opted_in", "opted_out", "not_set"), default="not_set"
    )
    opted_in_at: Mapped[datetime | None] = mapped_column(DateTime)
    opted_out_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contact: Mapped["Contact"] = relationship(back_populates="channel_prefs")
    channel_type: Mapped["ChannelType"] = relationship()


class ContactMarketingSource(Base):
    __tablename__ = "contact_marketing_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    marketing_source_id: Mapped[int] = mapped_column(ForeignKey("marketing_sources.id"))
    source_detail: Mapped[str | None] = mapped_column(String(255))
    attributed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    contact: Mapped["Contact"] = relationship(back_populates="marketing_sources")
    marketing_source: Mapped["MarketingSource"] = relationship()


class ContactTagMap(Base):
    __tablename__ = "contact_tag_map"

    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tag: Mapped["Tag"] = relationship()


class ContactNote(Base):
    __tablename__ = "contact_notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contact: Mapped["Contact"] = relationship(back_populates="notes")


class ContactPreference(Base):
    __tablename__ = "contact_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    pref_key: Mapped[str] = mapped_column(String(100), nullable=False)
    pref_value: Mapped[str] = mapped_column(Text, nullable=False)
    data_source: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contact: Mapped["Contact"] = relationship(back_populates="preferences")


from app.models.lookups import (  # noqa: E402
    AddressType,
    ChannelType,
    ContactType,
    EmailType,
    MarketingSource,
    PhoneType,
    Tag,
)
from app.models.organization import Organization  # noqa: E402
from app.models.source import Source  # noqa: E402
