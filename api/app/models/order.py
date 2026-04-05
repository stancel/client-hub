from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.lookups import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    order_status_id: Mapped[int] = mapped_column(ForeignKey("order_statuses.id"))
    order_number: Mapped[str | None] = mapped_column(String(50), unique=True)
    order_date: Mapped[str] = mapped_column(String(10), nullable=False)
    due_date: Mapped[str | None] = mapped_column(String(10))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    notes_text: Mapped[str | None] = mapped_column(Text)
    external_refs_json: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[str | None] = mapped_column(String(100))

    contact: Mapped["Contact"] = relationship(back_populates="orders")
    order_status: Mapped["OrderStatus"] = relationship()
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    invoices: Mapped[list] = relationship("Invoice", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    item_type_id: Mapped[int] = mapped_column(ForeignKey("order_item_types.id"))
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    notes_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    order: Mapped["Order"] = relationship(back_populates="items")
    item_type: Mapped["OrderItemType"] = relationship()


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    from_status_id: Mapped[int | None] = mapped_column(ForeignKey("order_statuses.id"))
    to_status_id: Mapped[int] = mapped_column(ForeignKey("order_statuses.id"))
    changed_by: Mapped[str | None] = mapped_column(String(100))
    notes_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    order: Mapped["Order"] = relationship(back_populates="status_history")
    from_status: Mapped["OrderStatus | None"] = relationship(foreign_keys=[from_status_id])
    to_status: Mapped["OrderStatus"] = relationship(foreign_keys=[to_status_id])


from app.models.contact import Contact  # noqa: E402
from app.models.lookups import OrderItemType, OrderStatus  # noqa: E402
