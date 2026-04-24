from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import SourceContext, require_api_key
from app.models.contact import ContactPreference
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    MarketingOptOuts,
    PreferenceSet,
)
from app.services.contact_service import (
    convert_contact,
    create_contact,
    deserialize_external_refs,
    get_contact_by_uuid,
    get_contact_summary,
    list_contacts,
    serialize_external_refs,
)

router = APIRouter(prefix="/contacts", tags=["contacts"], dependencies=[Depends(require_api_key)])


@router.get("")
async def list_contacts_endpoint(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    type: str | None = None,
    enrichment_status: str | None = None,
    search: str | None = None,
    is_active: bool = True,
    sort: str = "last_name",
    order: str = "asc",
    db: AsyncSession = Depends(get_db),
):
    return await list_contacts(
        db, page=page, per_page=per_page, contact_type=type,
        enrichment_status=enrichment_status, search=search,
        is_active=is_active, sort=sort, order=order,
    )


@router.get("/{uuid}")
async def get_contact_endpoint(uuid: str, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")

    from app.services.affiliation_service import serialize_affiliation

    active_affiliations = [a for a in contact.affiliations if a.is_active]
    primary_aff = next((a for a in active_affiliations if a.is_primary), None)
    affiliation_uuid_by_id = {a.id: a.uuid for a in contact.affiliations}

    return {
        "uuid": contact.uuid,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "display_name": contact.display_name,
        "contact_type": contact.contact_type.code,
        "primary_organization_uuid": primary_aff.organization.uuid if primary_aff else None,
        "primary_organization_name": primary_aff.organization.name if primary_aff else None,
        "primary_role_title": primary_aff.role_title if primary_aff else None,
        "primary_department": primary_aff.department if primary_aff else None,
        "affiliations": [serialize_affiliation(a) for a in active_affiliations],
        "enrichment_status": contact.enrichment_status,
        "marketing_opt_out_sms": contact.marketing_opt_out_sms,
        "marketing_opt_out_email": contact.marketing_opt_out_email,
        "marketing_opt_out_phone": contact.marketing_opt_out_phone,
        "phones": [
            {
                "number": p.phone_number,
                "type": p.phone_type.code,
                "is_primary": p.is_primary,
                "is_verified": p.is_verified,
                "affiliation_uuid": affiliation_uuid_by_id.get(p.affiliation_id) if p.affiliation_id else None,
            }
            for p in contact.phones
        ],
        "emails": [
            {
                "address": e.email_address,
                "type": e.email_type.code,
                "is_primary": e.is_primary,
                "is_verified": e.is_verified,
                "affiliation_uuid": affiliation_uuid_by_id.get(e.affiliation_id) if e.affiliation_id else None,
            }
            for e in contact.emails
        ],
        "tags": [tm.tag.label for tm in contact.tags],
        "marketing_sources": [ms.marketing_source.label for ms in contact.marketing_sources],
        "channel_preferences": {
            cp.channel_type.code: {"preferred": cp.is_preferred, "opt_in": cp.opt_in_status}
            for cp in contact.channel_prefs
        },
        "preferences": {p.pref_key: p.pref_value for p in contact.preferences},
        "notes": [
            {"text": n.note_text, "created_by": n.created_by, "created_at": n.created_at.isoformat()}
            for n in contact.notes
        ],
        "external_refs_json": deserialize_external_refs(contact.external_refs_json),
        "is_active": contact.is_active,
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
    }


@router.post("", status_code=201)
async def create_contact_endpoint(
    body: ContactCreate,
    ctx: SourceContext = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    try:
        contact = await create_contact(db, body.model_dump(), source_id=ctx.source_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "uuid": contact.uuid,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "external_refs_json": deserialize_external_refs(contact.external_refs_json),
    }


@router.put("/{uuid}")
async def update_contact_endpoint(uuid: str, body: ContactUpdate, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")

    update_data = body.model_dump(exclude_unset=True)
    if "external_refs_json" in update_data:
        contact.external_refs_json = serialize_external_refs(update_data.pop("external_refs_json"))
    for field, value in update_data.items():
        if hasattr(contact, field):
            setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return {"uuid": contact.uuid, "status": "updated"}


@router.delete("/{uuid}", status_code=204)
async def delete_contact_endpoint(uuid: str, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")

    from datetime import datetime, timezone
    contact.is_active = False
    contact.deleted_at = datetime.now(timezone.utc)
    await db.commit()


@router.post("/{uuid}/convert")
async def convert_contact_endpoint(uuid: str, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")
    if contact.contact_type.code == "client":
        raise HTTPException(status_code=400, detail="Contact is already a client")

    contact = await convert_contact(db, contact)
    # Reload to get updated type
    contact = await get_contact_by_uuid(db, uuid)
    return {
        "uuid": contact.uuid,
        "contact_type": contact.contact_type.code,
        "converted_at": contact.converted_at.isoformat() if contact.converted_at else None,
    }


@router.get("/{uuid}/summary")
async def contact_summary_endpoint(uuid: str, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")
    return await get_contact_summary(db, contact)


@router.get("/{uuid}/marketing")
async def get_marketing_optouts(uuid: str, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")
    return {
        "opt_out_sms": contact.marketing_opt_out_sms,
        "opt_out_email": contact.marketing_opt_out_email,
        "opt_out_phone": contact.marketing_opt_out_phone,
    }


@router.put("/{uuid}/marketing")
async def update_marketing_optouts(uuid: str, body: MarketingOptOuts, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")

    contact.marketing_opt_out_sms = body.opt_out_sms
    contact.marketing_opt_out_email = body.opt_out_email
    contact.marketing_opt_out_phone = body.opt_out_phone
    await db.commit()
    return {
        "opt_out_sms": contact.marketing_opt_out_sms,
        "opt_out_email": contact.marketing_opt_out_email,
        "opt_out_phone": contact.marketing_opt_out_phone,
    }


@router.get("/{uuid}/preferences")
async def list_preferences(uuid: str, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")
    return [
        {"key": p.pref_key, "value": p.pref_value, "data_source": p.data_source}
        for p in contact.preferences
    ]


@router.put("/{uuid}/preferences/{key}")
async def set_preference(uuid: str, key: str, body: PreferenceSet, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")

    # Find existing or create
    existing = next((p for p in contact.preferences if p.pref_key == key), None)
    if existing:
        existing.pref_value = body.value
        existing.data_source = body.data_source
    else:
        contact.preferences.append(ContactPreference(
            pref_key=key, pref_value=body.value, data_source=body.data_source,
        ))

    await db.commit()
    return {"key": key, "value": body.value, "data_source": body.data_source}


@router.delete("/{uuid}/preferences/{key}", status_code=204)
async def delete_preference(uuid: str, key: str, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_uuid(db, uuid)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {uuid} not found")

    pref = next((p for p in contact.preferences if p.pref_key == key), None)
    if not pref:
        raise HTTPException(status_code=404, detail=f"Preference '{key}' not found")

    await db.delete(pref)
    await db.commit()
