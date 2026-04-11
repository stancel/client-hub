from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.lookups import Base


class Communication(Base):
    __tablename__ = "communications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="RESTRICT"))
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"))
    channel_type_id: Mapped[int] = mapped_column(ForeignKey("channel_types.id"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))
    direction: Mapped[str] = mapped_column(Enum("inbound", "outbound"), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    external_message_id: Mapped[str | None] = mapped_column(String(255))
    created_by: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    source: Mapped["Source"] = relationship(foreign_keys=[source_id])
    contact: Mapped["Contact"] = relationship(back_populates="communications")
    channel_type: Mapped["ChannelType"] = relationship()


from app.models.contact import Contact  # noqa: E402
from app.models.lookups import ChannelType  # noqa: E402
from app.models.source import Source  # noqa: E402
