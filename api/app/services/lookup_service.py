from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.communication import Communication
from app.models.contact import (
    Contact,
    ContactChannelPref,
    ContactEmail,
    ContactPhone,
    ContactTagMap,
)
from app.models.order import Order
from app.services.phone_utils import PhoneNormalizationError, normalize_to_e164


async def lookup_by_phone(db: AsyncSession, phone_number: str, exact: bool = True):
    # Storage is E.164 (see app.services.phone_utils). Normalize the inbound
    # path parameter the same way so a SIP/CTI query of "8035551212" matches
    # a stored "+18035551212" — and so any pre-formatted "(803) 555-1212"
    # also resolves. If normalization fails (garbage input), the exact path
    # silently returns no matches; the substring path can still fuzzy-search.
    if exact:
        try:
            normalized = normalize_to_e164(phone_number)
        except PhoneNormalizationError:
            return []
        stmt = select(ContactPhone).where(ContactPhone.phone_number == normalized)
    else:
        # For substring search, reduce the input to digits only so callers
        # can paste any format and still get fuzzy matches against stored
        # E.164 values.
        digits = "".join(ch for ch in phone_number if ch.isdigit())
        needle = digits or phone_number
        stmt = select(ContactPhone).where(ContactPhone.phone_number.like(f"%{needle}%"))

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
    from app.models.affiliation import ContactOrgAffiliation as COAModel
    from app.models.contact import ContactEmail as CEModel
    from app.models.contact import ContactPhone as CPModel

    stmt = (
        select(Contact)
        .where(Contact.id.in_(contact_ids))
        .options(
            selectinload(Contact.contact_type),
            selectinload(Contact.affiliations).selectinload(COAModel.organization),
            selectinload(Contact.tags).selectinload(ContactTagMap.tag),
            selectinload(Contact.channel_prefs).selectinload(ContactChannelPref.channel_type),
            selectinload(Contact.phones).selectinload(CPModel.phone_type),
            selectinload(Contact.emails).selectinload(CEModel.email_type),
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

        # Include ALL phones and emails (not just the matched one)
        all_phones = [
            {"number": p.phone_number, "type": p.phone_type.code, "is_primary": p.is_primary, "is_verified": p.is_verified}
            for p in c.phones
        ]
        all_emails = [
            {"address": e.email_address, "type": e.email_type.code, "is_primary": e.is_primary, "is_verified": e.is_verified}
            for e in c.emails
        ]

        # Matched phone/email for quick reference
        phone_info = None
        if phone_map and c.id in phone_map:
            p = phone_map[c.id]
            phone_info = {"number": p.phone_number, "type": "phone", "is_primary": p.is_primary, "is_verified": p.is_verified}

        email_info = None
        if email_map and c.id in email_map:
            e = email_map[c.id]
            email_info = {"address": e.email_address, "type": "email", "is_primary": e.is_primary, "is_verified": e.is_verified}

        primary_aff = next(
            (a for a in c.affiliations if a.is_primary and a.is_active), None
        )
        matches.append({
            "uuid": c.uuid,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "display_name": c.display_name,
            "contact_type": c.contact_type.code,
            "organization": primary_aff.organization.name if primary_aff else None,
            "phone": phone_info,
            "email": email_info,
            "phones": all_phones,
            "emails": all_emails,
            "recent_orders": recent_orders,
            "recent_communications": recent_comms,
            "tags": tags,
            "channel_preferences": channel_prefs,
        })

    return matches
