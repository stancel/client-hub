import json
import logging
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.affiliation import ContactOrgAffiliation
from app.models.communication import Communication
from app.models.contact import (
    Contact,
    ContactChannelPref,
    ContactEmail,
    ContactMarketingSource,
    ContactPhone,
    ContactTagMap,
)
from app.models.invoice import Invoice
from app.models.lookups import ContactType, EmailType, PhoneType
from app.models.order import Order
from app.services.affiliation_service import (
    create_affiliation,
    get_primary_affiliation,
)
from app.services.marketing_source_service import (
    attach_codes as attach_marketing_codes,
)
from app.services.marketing_source_service import (
    derive_codes as derive_marketing_codes,
)

logger = logging.getLogger(__name__)


def serialize_external_refs(value: dict[str, Any] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value)


def deserialize_external_refs(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        logger.warning("Failed to parse external_refs_json; returning None")
        return None


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
            selectinload(Contact.first_seen_source),
            selectinload(Contact.affiliations).selectinload(ContactOrgAffiliation.organization),
            selectinload(Contact.affiliations).selectinload(ContactOrgAffiliation.seniority_level),
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


async def create_contact(db: AsyncSession, data: dict, source_id: int | None = None) -> Contact:
    # Resolve contact type
    ct_result = await db.execute(select(ContactType).where(ContactType.code == data["contact_type"]))
    ct = ct_result.scalar_one_or_none()
    if not ct:
        raise ValueError(f"Unknown contact type: {data['contact_type']}")

    # Resolve source_id — use provided or fall back to bootstrap
    if source_id is None:
        from app.models.source import Source
        bootstrap = (await db.execute(select(Source).where(Source.code == "bootstrap"))).scalar_one()
        source_id = bootstrap.id

    contact = Contact(
        uuid=str(uuid_mod.uuid4()),
        contact_type_id=ct.id,
        first_seen_source_id=source_id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        display_name=data.get("display_name"),
        enrichment_status="partial",
        external_refs_json=serialize_external_refs(data.get("external_refs_json")),
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

    # Marketing sources — explicit list from the payload wins; if empty,
    # derive from external_refs_json (UTM params + referrer hostname)
    # so the contact_marketing_sources junction is never empty when we
    # have any signal. See app.services.marketing_source_service.
    explicit_codes = list(data.get("marketing_sources") or [])
    if explicit_codes:
        await attach_marketing_codes(
            db, contact, explicit_codes, source_detail="explicit",
        )
    else:
        derived_codes = derive_marketing_codes(data.get("external_refs_json"))
        await attach_marketing_codes(
            db, contact, derived_codes, source_detail="derived",
        )

    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    # Affiliations — created after the contact exists so each affiliation
    # can reference contact.id. create_affiliation commits its own row.
    for aff_data in data.get("affiliations", []) or []:
        await create_affiliation(
            db, contact, aff_data, created_by=data.get("data_source", "api")
        )

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

    # Primary affiliation (org, role, department)
    primary_aff = await get_primary_affiliation(db, contact.id)
    primary_org_uuid = primary_aff.organization.uuid if primary_aff else None
    primary_org_name = primary_aff.organization.name if primary_aff else None
    primary_role_title = primary_aff.role_title if primary_aff else None
    primary_department = primary_aff.department if primary_aff else None

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
        "primary_organization_uuid": primary_org_uuid,
        "primary_organization_name": primary_org_name,
        "primary_role_title": primary_role_title,
        "primary_department": primary_department,
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
