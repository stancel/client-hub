from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_api_key
from app.models.business import BusinessSettings

router = APIRouter(prefix="/settings", tags=["settings"], dependencies=[Depends(require_api_key)])


class SettingsUpdate(BaseModel):
    business_name: str | None = None
    business_type: str | None = None
    timezone: str | None = None
    currency: str | None = None
    tax_rate: float | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None


@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessSettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Business settings not configured")
    return {
        "business_name": settings.business_name,
        "business_type": settings.business_type,
        "timezone": settings.timezone,
        "currency": settings.currency,
        "tax_rate": float(settings.tax_rate) if settings.tax_rate else None,
        "phone": settings.phone,
        "email": settings.email,
        "website": settings.website,
        "address": {
            "line1": settings.address_line1,
            "line2": settings.address_line2,
            "city": settings.city,
            "state": settings.state,
            "postal_code": settings.postal_code,
            "country": settings.country,
        },
    }


@router.put("")
async def update_settings(body: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessSettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Business settings not configured")

    for field, value in body.model_dump(exclude_unset=True).items():
        if hasattr(settings, field):
            setattr(settings, field, value)

    await db.commit()
    return {"status": "updated"}
