"""Public read of the canonical marketing-source list.

Source-key gated, mirrors the ``/spam-patterns`` pattern. Consumer
sites pull this at build/deploy time so the per-site filter logic
matches Client Hub's lookup table without hardcoding the codes.

Admin CRUD on the underlying ``marketing_sources`` table is not
exposed here — the lookup is seed-only (migration 011); changes
flow through migrations and are reviewed.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_api_key
from app.services.marketing_source_service import list_active_marketing_sources

public_router = APIRouter(
    prefix="/marketing-sources",
    tags=["marketing-sources"],
    dependencies=[Depends(require_api_key)],
)


@public_router.get("")
async def get_active_marketing_sources(
    db: AsyncSession = Depends(get_db),
):
    """Return ``[{"code": ..., "label": ...}, ...]`` for active rows."""
    return {"data": await list_active_marketing_sources(db)}
