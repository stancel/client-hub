from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contact import (
    Contact,
    ContactChannelPref,
    ContactEmail,
    ContactMarketingSource,
    ContactPhone,
    ContactTagMap,
)
from app.models.communication import Communication
from app.models.order import Order


async def lookup_by_phone(db: AsyncSession, phone_number: str, exact: bool = True):
    if exact:
        stmt = select(ContactPhone).where(ContactPhone.phone_number == phone_number)
    else:
        stmt = select(ContactPhone).where(ContactPhone.phone_number.like(f"%{phone_number}%"))

    result = await db.execute(stmt)
    phone_rows = result.scalars().all()

    if not phone_rows:
        return []

    contact_ids = [p.contact_id for p in phone_rows]
    phone_map = {p.contact_id: p for p in phone_rows}

    return await _build_match_results(db, contact_ids, phone_map=phone_map)


async def lookup_by_email(db: AsyncSession, email_address: str, exact: bool = True):
    if exact:
        stmt = select(ContactEmail).where(ContactEmail.email_address == email_address)
    else:
        stmt = select(ContactEmail).where(ContactEmail.email_address.like(f"%{email_address}%"))

    result = await db.execute(stmt)
    email_rows = result.scalars().all()

    if not email_rows:
        return []

    contact_ids = [e.contact_id for e in email_rows]
    email_map = {e.contact_id: e for e in email_rows}

    return await _build_match_results(db, contact_ids, email_map=email_map)


async def _build_match_results(
    db: AsyncSession,
    contact_ids: list[int],
    phone_map: dict | None = None,
    email_map: dict | None = None,
):
    stmt = (
        select(Contact)
        .where(Contact.id.in_(contact_ids))
        .options(
            selectinload(Contact.contact_type),
            selectinload(Contact.organization),
            selectinload(Contact.tags).selectinload(ContactTagMap.tag),
            selectinload(Contact.channel_prefs).selectinload(ContactChannelPref.channel_type),
        )
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    matches = []
    for c in contacts:
        # Recent orders (last 5)
        order_stmt = (
            select(Order)
            .where(Order.contact_id == c.id, Order.is_active == True)  # noqa: E712
            .order_by(Order.order_date.desc())
            .limit(5)
        )
        order_result = await db.execute(
            order_stmt.options(selectinload(Order.order_status))
        )
        recent_orders = [
            {
                "order_number": o.order_number,
                "status": o.order_status.code,
                "total": str(o.total),
                "order_date": str(o.order_date),
            }
            for o in order_result.scalars().all()
        ]

        # Recent communications (last 5)
        comm_stmt = (
            select(Communication)
            .where(Communication.contact_id == c.id)
            .order_by(Communication.occurred_at.desc())
            .limit(5)
        )
        comm_result = await db.execute(
            comm_stmt.options(selectinload(Communication.channel_type))
        )
        recent_comms = [
            {
                "channel": cm.channel_type.code,
                "direction": cm.direction,
                "subject": cm.subject,
                "occurred_at": cm.occurred_at.isoformat() if cm.occurred_at else None,
            }
            for cm in comm_result.scalars().all()
        ]

        # Tags
        tags = [tm.tag.label for tm in c.tags]

        # Channel preferences
        channel_prefs = {}
        for cp in c.channel_prefs:
            channel_prefs[cp.channel_type.code] = {
                "preferred": cp.is_preferred,
                "opt_in": cp.opt_in_status,
            }

        # Build phone/email info from matched row
        phone_info = None
        if phone_map and c.id in phone_map:
            p = phone_map[c.id]
            phone_type_stmt = select(Contact).where(Contact.id == c.id)  # placeholder
            # Load phone type
            from app.models.lookups import PhoneType
            pt_result = await db.execute(select(PhoneType).where(PhoneType.id == p.phone_type_id))
            pt = pt_result.scalar_one_or_none()
            phone_info = {
                "number": p.phone_number,
                "type": pt.code if pt else "unknown",
                "is_primary": p.is_primary,
                "is_verified": p.is_verified,
            }

        email_info = None
        if email_map and c.id in email_map:
            e = email_map[c.id]
            from app.models.lookups import EmailType
            et_result = await db.execute(select(EmailType).where(EmailType.id == e.email_type_id))
            et = et_result.scalar_one_or_none()
            email_info = {
                "address": e.email_address,
                "type": et.code if et else "unknown",
                "is_primary": e.is_primary,
                "is_verified": e.is_verified,
            }

        matches.append({
            "uuid": c.uuid,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "display_name": c.display_name,
            "contact_type": c.contact_type.code,
            "organization": c.organization.name if c.organization else None,
            "phone": phone_info,
            "email": email_info,
            "recent_orders": recent_orders,
            "recent_communications": recent_comms,
            "tags": tags,
            "channel_preferences": channel_prefs,
        })

    return matches
