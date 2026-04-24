import json
import logging
import uuid as uuid_mod
from typing import Any

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.affiliation import ContactOrgAffiliation, SeniorityLevel
from app.models.contact import Contact
from app.models.organization import Organization

logger = logging.getLogger(__name__)


async def _resolve_seniority_id(db: AsyncSession, code: str | None) -> int | None:
    if not code:
        return None
    row = (
        await db.execute(select(SeniorityLevel).where(SeniorityLevel.code == code))
    ).scalar_one_or_none()
    return row.id if row else None


async def _resolve_seniority_code(db: AsyncSession, sid: int | None) -> str | None:
    if not sid:
        return None
    row = (
        await db.execute(select(SeniorityLevel).where(SeniorityLevel.id == sid))
    ).scalar_one_or_none()
    return row.code if row else None


async def _load_affiliations_for_contact(
    db: AsyncSession, contact_id: int, active_only: bool = True
) -> list[ContactOrgAffiliation]:
    stmt = (
        select(ContactOrgAffiliation)
        .where(ContactOrgAffiliation.contact_id == contact_id)
        .options(
            selectinload(ContactOrgAffiliation.organization),
            selectinload(ContactOrgAffiliation.seniority_level),
        )
        .order_by(
            ContactOrgAffiliation.is_primary.desc(),
            ContactOrgAffiliation.start_date.is_(None),
            ContactOrgAffiliation.start_date.desc(),
            ContactOrgAffiliation.id.asc(),
        )
    )
    if active_only:
        stmt = stmt.where(ContactOrgAffiliation.is_active == True)  # noqa: E712
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _demote_other_primaries(db: AsyncSession, contact_id: int, keep_id: int | None) -> None:
    """Set is_primary=FALSE on all rows for this contact except the keep_id row.

    Must run before setting a new primary to satisfy the ux_coa_one_primary
    unique constraint.
    """
    stmt = (
        update(ContactOrgAffiliation)
        .where(
            and_(
                ContactOrgAffiliation.contact_id == contact_id,
                ContactOrgAffiliation.is_primary == True,  # noqa: E712
            )
        )
        .values(is_primary=False)
    )
    if keep_id is not None:
        stmt = stmt.where(ContactOrgAffiliation.id != keep_id)
    await db.execute(stmt)


async def get_primary_affiliation(
    db: AsyncSession, contact_id: int
) -> ContactOrgAffiliation | None:
    stmt = (
        select(ContactOrgAffiliation)
        .where(
            ContactOrgAffiliation.contact_id == contact_id,
            ContactOrgAffiliation.is_primary == True,  # noqa: E712
            ContactOrgAffiliation.is_active == True,  # noqa: E712
        )
        .options(selectinload(ContactOrgAffiliation.organization))
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def list_affiliations(
    db: AsyncSession, contact: Contact, active_only: bool = True
) -> dict:
    rows = await _load_affiliations_for_contact(db, contact.id, active_only=active_only)
    return {
        "data": [_serialize(r) for r in rows],
        "count": len(rows),
    }


async def create_affiliation(
    db: AsyncSession, contact: Contact, data: dict, created_by: str | None = None
) -> ContactOrgAffiliation:
    org = (
        await db.execute(
            select(Organization).where(Organization.uuid == data["organization_uuid"])
        )
    ).scalar_one_or_none()
    if not org:
        raise ValueError(f"Unknown organization_uuid: {data['organization_uuid']}")

    seniority_id = await _resolve_seniority_id(db, data.get("seniority"))

    is_primary = bool(data.get("is_primary", False))

    aff = ContactOrgAffiliation(
        uuid=str(uuid_mod.uuid4()),
        contact_id=contact.id,
        organization_id=org.id,
        role_title=data.get("role_title"),
        department=data.get("department"),
        seniority_level_id=seniority_id,
        is_decision_maker=bool(data.get("is_decision_maker", False)),
        is_primary=False,  # set after demote to satisfy unique index
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        is_active=True,
        notes_text=data.get("notes"),
        external_refs_json=(
            json.dumps(data["external_refs_json"])
            if data.get("external_refs_json") is not None
            else None
        ),
        created_by=created_by or "api",
    )
    db.add(aff)
    await db.flush()  # assign aff.id

    if is_primary:
        await _demote_other_primaries(db, contact.id, keep_id=aff.id)
        aff.is_primary = True

    await db.commit()
    await db.refresh(aff, attribute_names=["organization", "seniority_level"])
    return aff


async def update_affiliation(
    db: AsyncSession, aff: ContactOrgAffiliation, data: dict
) -> ContactOrgAffiliation:
    simple_fields = {
        "role_title",
        "department",
        "is_decision_maker",
        "start_date",
        "end_date",
        "is_active",
    }
    for field in simple_fields:
        if field in data and data[field] is not None:
            setattr(aff, field, data[field])

    if "notes" in data and data["notes"] is not None:
        aff.notes_text = data["notes"]

    if "seniority" in data and data["seniority"] is not None:
        aff.seniority_level_id = await _resolve_seniority_id(db, data["seniority"])

    if "external_refs_json" in data and data["external_refs_json"] is not None:
        aff.external_refs_json = json.dumps(data["external_refs_json"])

    if "is_primary" in data and data["is_primary"] is not None:
        want_primary = bool(data["is_primary"])
        if want_primary and not aff.is_primary:
            await _demote_other_primaries(db, aff.contact_id, keep_id=aff.id)
            aff.is_primary = True
        elif not want_primary and aff.is_primary:
            aff.is_primary = False

    await db.commit()
    await db.refresh(aff, attribute_names=["organization", "seniority_level"])
    return aff


async def delete_affiliation(db: AsyncSession, aff: ContactOrgAffiliation) -> None:
    was_primary = aff.is_primary
    contact_id = aff.contact_id
    await db.delete(aff)
    await db.flush()

    if was_primary:
        # Promote the most-recent active affiliation to primary.
        candidate_stmt = (
            select(ContactOrgAffiliation)
            .where(
                ContactOrgAffiliation.contact_id == contact_id,
                ContactOrgAffiliation.is_active == True,  # noqa: E712
            )
            .order_by(
                ContactOrgAffiliation.start_date.is_(None),
            ContactOrgAffiliation.start_date.desc(),
                ContactOrgAffiliation.id.desc(),
            )
            .limit(1)
        )
        candidate = (await db.execute(candidate_stmt)).scalar_one_or_none()
        if candidate is not None:
            candidate.is_primary = True

    await db.commit()


async def get_affiliation_by_uuid(
    db: AsyncSession, contact_id: int, aff_uuid: str
) -> ContactOrgAffiliation | None:
    stmt = (
        select(ContactOrgAffiliation)
        .where(
            ContactOrgAffiliation.uuid == aff_uuid,
            ContactOrgAffiliation.contact_id == contact_id,
        )
        .options(
            selectinload(ContactOrgAffiliation.organization),
            selectinload(ContactOrgAffiliation.seniority_level),
        )
    )
    return (await db.execute(stmt)).scalar_one_or_none()


def _serialize(aff: ContactOrgAffiliation) -> dict[str, Any]:
    return {
        "uuid": aff.uuid,
        "organization": (
            {"uuid": aff.organization.uuid, "name": aff.organization.name}
            if aff.organization is not None
            else None
        ),
        "organization_uuid": aff.organization.uuid if aff.organization else None,
        "role_title": aff.role_title,
        "department": aff.department,
        "seniority": aff.seniority_level.code if aff.seniority_level else None,
        "is_decision_maker": bool(aff.is_decision_maker),
        "is_primary": bool(aff.is_primary),
        "start_date": aff.start_date.isoformat() if aff.start_date else None,
        "end_date": aff.end_date.isoformat() if aff.end_date else None,
        "is_active": bool(aff.is_active),
        "notes": aff.notes_text,
        "created_at": aff.created_at.isoformat() if aff.created_at else None,
    }


def serialize_affiliation(aff: ContactOrgAffiliation) -> dict[str, Any]:
    """Public alias so routers/services can build response payloads."""
    return _serialize(aff)
