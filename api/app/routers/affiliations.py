from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import SourceContext, require_api_key
from app.schemas.affiliation import AffiliationCreate, AffiliationUpdate
from app.services.affiliation_service import (
    create_affiliation,
    delete_affiliation,
    get_affiliation_by_uuid,
    list_affiliations,
    serialize_affiliation,
    update_affiliation,
)
from app.services.contact_service import get_contact_by_uuid

router = APIRouter(
    prefix="/contacts/{contact_uuid}/affiliations",
    tags=["affiliations"],
    dependencies=[Depends(require_api_key)],
)


async def _load_contact(db: AsyncSession, contact_uuid: str):
    contact = await get_contact_by_uuid(db, contact_uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {contact_uuid} not found")
    return contact


@router.get("")
async def list_affiliations_endpoint(
    contact_uuid: str,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    contact = await _load_contact(db, contact_uuid)
    return await list_affiliations(db, contact, active_only=active_only)


@router.post("", status_code=201)
async def create_affiliation_endpoint(
    contact_uuid: str,
    body: AffiliationCreate,
    ctx: SourceContext = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    contact = await _load_contact(db, contact_uuid)
    try:
        aff = await create_affiliation(
            db, contact, body.model_dump(exclude_unset=True),
            created_by="root" if ctx.is_root else f"source:{ctx.source_id}",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return serialize_affiliation(aff)


@router.put("/{affiliation_uuid}")
async def update_affiliation_endpoint(
    contact_uuid: str,
    affiliation_uuid: str,
    body: AffiliationUpdate,
    db: AsyncSession = Depends(get_db),
):
    contact = await _load_contact(db, contact_uuid)
    aff = await get_affiliation_by_uuid(db, contact.id, affiliation_uuid)
    if not aff:
        raise HTTPException(
            status_code=404,
            detail=f"Affiliation {affiliation_uuid} not found for contact {contact_uuid}",
        )
    try:
        aff = await update_affiliation(db, aff, body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return serialize_affiliation(aff)


@router.delete("/{affiliation_uuid}", status_code=204)
async def delete_affiliation_endpoint(
    contact_uuid: str,
    affiliation_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    contact = await _load_contact(db, contact_uuid)
    aff = await get_affiliation_by_uuid(db, contact.id, affiliation_uuid)
    if not aff:
        raise HTTPException(
            status_code=404,
            detail=f"Affiliation {affiliation_uuid} not found for contact {contact_uuid}",
        )
    await delete_affiliation(db, aff)
