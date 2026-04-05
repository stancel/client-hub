import uuid as uuid_mod
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contact import (
    Contact,
    ContactChannelPref,
    ContactEmail,
    ContactMarketingSource,
    ContactPhone,
    ContactPreference,
    ContactTagMap,
)
from app.models.lookups import ContactType, MarketingSource, PhoneType, EmailType
from app.models.order import Order
from app.models.invoice import Invoice
from app.models.communication import Communication


async def list_contacts(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 25,
    contact_type: str | None = None,
    enrichment_status: str | None = None,
    search: str | None = None,
    is_active: bool = True,
    sort: str = "last_name",
    order: str = "asc",
):
    stmt = select(Contact).where(Contact.is_active == is_active)

    if contact_type:
        stmt = stmt.join(ContactType, Contact.contact_type_id == ContactType.id).where(ContactType.code == contact_type)

    if enrichment_status:
        stmt = stmt.where(Contact.enrichment_status == enrichment_status)

    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            (Contact.first_name.like(like))
            | (Contact.last_name.like(like))
        )

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Sort
    sort_col = getattr(Contact, sort, Contact.last_name)
    stmt = stmt.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

    # Paginate
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    stmt = stmt.options(selectinload(Contact.contact_type))

    result = await db.execute(stmt)
    contacts = result.scalars().all()

    return {
        "data": [
            {
                "uuid": c.uuid,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "display_name": c.display_name,
                "contact_type": c.contact_type.code,
                "enrichment_status": c.enrichment_status,
                "is_active": c.is_active,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in contacts
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if per_page else 0,
        },
    }


async def get_contact_by_uuid(db: AsyncSession, contact_uuid: str) -> Contact | None:
    stmt = (
        select(Contact)
        .where(Contact.uuid == contact_uuid)
        .options(
            selectinload(Contact.contact_type),
            selectinload(Contact.organization),
            selectinload(Contact.phones).selectinload(ContactPhone.phone_type),
            selectinload(Contact.emails).selectinload(ContactEmail.email_type),
            selectinload(Contact.addresses),
            selectinload(Contact.channel_prefs).selectinload(ContactChannelPref.channel_type),
            selectinload(Contact.marketing_sources).selectinload(ContactMarketingSource.marketing_source),
            selectinload(Contact.tags).selectinload(ContactTagMap.tag),
            selectinload(Contact.notes),
            selectinload(Contact.preferences),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(db: AsyncSession, data: dict) -> Contact:
    # Resolve contact type
    ct_result = await db.execute(select(ContactType).where(ContactType.code == data["contact_type"]))
    ct = ct_result.scalar_one_or_none()
    if not ct:
        raise ValueError(f"Unknown contact type: {data['contact_type']}")

    contact = Contact(
        uuid=str(uuid_mod.uuid4()),
        contact_type_id=ct.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        display_name=data.get("display_name"),
        enrichment_status="partial",
        created_by=data.get("data_source", "api"),
    )

    # Phones
    for p in data.get("phones", []):
        pt_result = await db.execute(select(PhoneType).where(PhoneType.code == p["type"]))
        pt = pt_result.scalar_one_or_none()
        if pt:
            contact.phones.append(ContactPhone(
                phone_type_id=pt.id,
                phone_number=p["number"],
                is_primary=p.get("is_primary", False),
                data_source=data.get("data_source"),
            ))

    # Emails
    for e in data.get("emails", []):
        et_result = await db.execute(select(EmailType).where(EmailType.code == e["type"]))
        et = et_result.scalar_one_or_none()
        if et:
            contact.emails.append(ContactEmail(
                email_type_id=et.id,
                email_address=e["address"],
                is_primary=e.get("is_primary", False),
                data_source=data.get("data_source"),
            ))

    # Marketing sources
    for src_code in data.get("marketing_sources", []):
        ms_result = await db.execute(select(MarketingSource).where(MarketingSource.code == src_code))
        ms = ms_result.scalar_one_or_none()
        if ms:
            contact.marketing_sources.append(ContactMarketingSource(
                marketing_source_id=ms.id,
                attributed_at=datetime.now(timezone.utc),
            ))

    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def convert_contact(db: AsyncSession, contact: Contact, notes: str | None = None) -> Contact:
    client_type = (await db.execute(select(ContactType).where(ContactType.code == "client"))).scalar_one()

    contact.converted_from_type_id = contact.contact_type_id
    contact.contact_type_id = client_type.id
    contact.converted_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contact_summary(db: AsyncSession, contact: Contact) -> dict:
    # Primary phone
    primary_phone = None
    for p in contact.phones:
        if p.is_primary:
            primary_phone = p.phone_number
            break

    # Primary email
    primary_email = None
    for e in contact.emails:
        if e.is_primary:
            primary_email = e.email_address
            break

    # Order stats
    order_stmt = select(
        func.count(Order.id),
        func.coalesce(func.sum(Order.total), 0),
        func.max(Order.order_date),
    ).where(Order.contact_id == contact.id, Order.is_active == True)  # noqa: E712
    order_result = (await db.execute(order_stmt)).one()

    # Communication stats
    comm_stmt = select(
        func.count(Communication.id),
        func.max(Communication.occurred_at),
    ).where(Communication.contact_id == contact.id)
    comm_result = (await db.execute(comm_stmt)).one()

    # Outstanding balance
    bal_stmt = select(
        func.coalesce(func.sum(Invoice.balance_due), 0)
    ).join(Order).where(
        Order.contact_id == contact.id, Invoice.is_active == True  # noqa: E712
    )
    outstanding = (await db.execute(bal_stmt)).scalar() or 0

    return {
        "uuid": contact.uuid,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "display_name": contact.display_name,
        "contact_type": contact.contact_type.code,
        "enrichment_status": contact.enrichment_status,
        "marketing_opt_out_sms": contact.marketing_opt_out_sms,
        "marketing_opt_out_email": contact.marketing_opt_out_email,
        "marketing_opt_out_phone": contact.marketing_opt_out_phone,
        "organization": contact.organization.name if contact.organization else None,
        "primary_phone": primary_phone,
        "primary_email": primary_email,
        "total_orders": order_result[0],
        "lifetime_value": str(order_result[1]),
        "last_order_date": str(order_result[2]) if order_result[2] else None,
        "total_communications": comm_result[0],
        "last_communication_at": comm_result[1].isoformat() if comm_result[1] else None,
        "outstanding_balance": str(outstanding),
        "marketing_sources": [ms.marketing_source.label for ms in contact.marketing_sources],
        "tags": [tm.tag.label for tm in contact.tags],
    }
