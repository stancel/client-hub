from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LookupMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class ContactType(LookupMixin, Base):
    __tablename__ = "contact_types"


class PhoneType(LookupMixin, Base):
    __tablename__ = "phone_types"


class EmailType(LookupMixin, Base):
    __tablename__ = "email_types"


class AddressType(LookupMixin, Base):
    __tablename__ = "address_types"


class ChannelType(LookupMixin, Base):
    __tablename__ = "channel_types"


class MarketingSource(LookupMixin, Base):
    __tablename__ = "marketing_sources"


class OrderStatus(LookupMixin, Base):
    __tablename__ = "order_statuses"


class OrderItemType(LookupMixin, Base):
    __tablename__ = "order_item_types"


class InvoiceStatus(LookupMixin, Base):
    __tablename__ = "invoice_statuses"


class PaymentMethod(LookupMixin, Base):
    __tablename__ = "payment_methods"


class Tag(LookupMixin, Base):
    __tablename__ = "tags"
