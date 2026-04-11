import secrets
import uuid as uuid_mod
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import require_root_key
from app.models.api_key import ApiKey
from app.models.source import Source

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_root_key)])


# --- Schemas ---

class SourceCreate(BaseModel):
    code: str
    name: str
    source_type: str = "website"
    domain: str | None = None
    description: str | None = None


class SourceUpdate(BaseModel):
    name: str | None = None
    source_type: str | None = None
    domain: str | None = None
    description: str | None = None


class ApiKeyCreate(BaseModel):
    name: str = "Default key"


# --- Source endpoints ---

@router.get("/sources")
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.code))
    sources = result.scalars().all()
    return {
        "data": [
            {
                "uuid": s.uuid, "code": s.code, "name": s.name,
                "source_type": s.source_type, "domain": s.domain,
                "is_active": s.is_active,
            }
            for s in sources
        ],
        "count": len(sources),
    }


@router.get("/sources/{uuid}")
async def get_source(uuid: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Source).where(Source.uuid == uuid).options(selectinload(Source.api_keys))
    source = (await db.execute(stmt)).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {uuid} not found")
    return {
        "uuid": source.uuid, "code": source.code, "name": source.name,
        "source_type": source.source_type, "domain": source.domain,
        "description": source.description, "is_active": source.is_active,
        "api_key_count": len([k for k in source.api_keys if k.is_active]),
    }


@router.post("/sources", status_code=201)
async def create_source(body: SourceCreate, db: AsyncSession = Depends(get_db)):
    # Check for duplicate code
    existing = (await db.execute(select(Source).where(Source.code == body.code))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail=f"Source code '{body.code}' already exists")

    source = Source(
        uuid=str(uuid_mod.uuid4()), code=body.code, name=body.name,
        source_type=body.source_type, domain=body.domain, description=body.description,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return {"uuid": source.uuid, "code": source.code, "name": source.name}


@router.put("/sources/{uuid}")
async def update_source(uuid: str, body: SourceUpdate, db: AsyncSession = Depends(get_db)):
    source = (await db.execute(select(Source).where(Source.uuid == uuid))).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {uuid} not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        if hasattr(source, field):
            setattr(source, field, value)
    await db.commit()
    return {"uuid": source.uuid, "status": "updated"}


@router.delete("/sources/{uuid}", status_code=204)
async def delete_source(uuid: str, db: AsyncSession = Depends(get_db)):
    source = (await db.execute(select(Source).where(Source.uuid == uuid))).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {uuid} not found")
    source.is_active = False
    await db.commit()


# --- API Key endpoints ---

@router.get("/sources/{uuid}/api-keys")
async def list_api_keys(uuid: str, db: AsyncSession = Depends(get_db)):
    source = (await db.execute(select(Source).where(Source.uuid == uuid))).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {uuid} not found")

    result = await db.execute(select(ApiKey).where(ApiKey.source_id == source.id).order_by(ApiKey.created_at))
    keys = result.scalars().all()
    return {
        "data": [
            {
                "uuid": k.uuid, "key_prefix": k.key_prefix, "name": k.name,
                "is_active": k.is_active, "created_at": k.created_at.isoformat() if k.created_at else None,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                "revoked_at": k.revoked_at.isoformat() if k.revoked_at else None,
            }
            for k in keys
        ],
        "count": len(keys),
    }


@router.post("/sources/{uuid}/api-keys", status_code=201)
async def create_api_key(uuid: str, body: ApiKeyCreate, db: AsyncSession = Depends(get_db)):
    source = (await db.execute(select(Source).where(Source.uuid == uuid))).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {uuid} not found")

    raw_key = secrets.token_hex(32)
    key_prefix = raw_key[:8]

    api_key = ApiKey(
        uuid=str(uuid_mod.uuid4()), source_id=source.id,
        key_prefix=key_prefix, key_value=raw_key, name=body.name,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    # Return the full key ONLY on creation — never again
    return {
        "uuid": api_key.uuid,
        "key_prefix": key_prefix,
        "key_value": raw_key,
        "name": api_key.name,
        "source_code": source.code,
        "warning": "Save this key now. It will not be shown again.",
    }


@router.delete("/api-keys/{uuid}", status_code=204)
async def revoke_api_key(uuid: str, db: AsyncSession = Depends(get_db)):
    api_key = (await db.execute(select(ApiKey).where(ApiKey.uuid == uuid))).scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail=f"API key {uuid} not found")
    api_key.is_active = False
    api_key.revoked_at = datetime.now(timezone.utc)
    await db.commit()
