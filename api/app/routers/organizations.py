import uuid as uuid_mod
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import require_api_key
from app.models.organization import OrgAddress, Organization, OrgEmail, OrgPhone

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(require_api_key)])


class OrgCreate(BaseModel):
    name: str
    org_type: str | None = None
    website: str | None = None


class OrgUpdate(BaseModel):
    name: str | None = None
    org_type: str | None = None
    website: str | None = None
    notes_text: str | None = None


@router.get("")
async def list_organizations(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    search: str | None = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Organization).where(Organization.is_active == is_active)
    if search:
        stmt = stmt.where(Organization.name.like(f"%{search}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Organization.name).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    orgs = result.scalars().all()

    return {
        "data": [
            {"uuid": o.uuid, "name": o.name, "org_type": o.org_type, "is_active": o.is_active}
            for o in orgs
        ],
        "pagination": {"page": page, "per_page": per_page, "total": total,
                        "total_pages": (total + per_page - 1) // per_page if per_page else 0},
    }


async def _get_org(db: AsyncSession, uuid: str) -> Organization | None:
    stmt = (
        select(Organization).where(Organization.uuid == uuid)
        .options(
            selectinload(Organization.phones).selectinload(OrgPhone.phone_type),
            selectinload(Organization.emails).selectinload(OrgEmail.email_type),
            selectinload(Organization.addresses).selectinload(OrgAddress.address_type),
            selectinload(Organization.contacts),
        )
    )
    return (await db.execute(stmt)).scalar_one_or_none()


@router.get("/{uuid}")
async def get_organization(uuid: str, db: AsyncSession = Depends(get_db)):
    org = await _get_org(db, uuid)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {uuid} not found")

    from app.models.contact import Contact
    contact_count = (await db.execute(
        select(func.count()).where(Contact.organization_id == org.id)
    )).scalar() or 0

    return {
        "uuid": org.uuid,
        "name": org.name,
        "org_type": org.org_type,
        "website": org.website,
        "phones": [{"number": p.phone_number, "type": p.phone_type.code, "is_primary": p.is_primary} for p in org.phones],
        "emails": [{"address": e.email_address, "type": e.email_type.code, "is_primary": e.is_primary} for e in org.emails],
        "addresses": [
            {"type": a.address_type.code, "address_line1": a.address_line1, "city": a.city,
             "state": a.state, "postal_code": a.postal_code, "is_primary": a.is_primary}
            for a in org.addresses
        ],
        "contact_count": contact_count,
        "is_active": org.is_active,
    }


@router.post("", status_code=201)
async def create_organization(body: OrgCreate, db: AsyncSession = Depends(get_db)):
    org = Organization(uuid=str(uuid_mod.uuid4()), name=body.name, org_type=body.org_type, website=body.website, created_by="api")
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return {"uuid": org.uuid, "name": org.name}


@router.put("/{uuid}")
async def update_organization(uuid: str, body: OrgUpdate, db: AsyncSession = Depends(get_db)):
    org = await _get_org(db, uuid)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {uuid} not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        if hasattr(org, field):
            setattr(org, field, value)
    await db.commit()
    return {"uuid": org.uuid, "status": "updated"}


@router.delete("/{uuid}", status_code=204)
async def delete_organization(uuid: str, db: AsyncSession = Depends(get_db)):
    org = await _get_org(db, uuid)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {uuid} not found")
    org.is_active = False
    org.deleted_at = datetime.now(timezone.utc)
    await db.commit()
