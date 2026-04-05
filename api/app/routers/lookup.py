from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_api_key
from app.services.lookup_service import lookup_by_email, lookup_by_phone

router = APIRouter(prefix="/lookup", tags=["lookup"], dependencies=[Depends(require_api_key)])


@router.get("/phone/{number}")
async def lookup_phone(
    number: str,
    exact: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    matches = await lookup_by_phone(db, number, exact=exact)
    if not matches:
        raise HTTPException(status_code=404, detail=f"No contact found for phone {number}")
    return {"matches": matches, "count": len(matches)}


@router.get("/email/{email:path}")
async def lookup_email(
    email: str,
    exact: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    matches = await lookup_by_email(db, email, exact=exact)
    if not matches:
        raise HTTPException(status_code=404, detail=f"No contact found for email {email}")
    return {"matches": matches, "count": len(matches)}
