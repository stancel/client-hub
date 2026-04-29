"""Spam-defense framework — admin + public routers.

Public read (source-key gated, used by consumer sites for build-time pattern sync):
    GET  /api/v1/spam-patterns

Admin (root-key gated):
    GET    /api/v1/admin/spam-patterns
    POST   /api/v1/admin/spam-patterns
    PUT    /api/v1/admin/spam-patterns/{uuid}
    DELETE /api/v1/admin/spam-patterns/{uuid}
    GET    /api/v1/admin/spam-events
    GET    /api/v1/admin/spam-events/stats
    POST   /api/v1/admin/spam-events/{uuid}/mark-false-positive
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import SourceContext, require_api_key, require_root_key
from app.schemas.spam import (
    SpamPatternCreate,
    SpamPatternUpdate,
)
from app.services.spam_filter_service import (
    _serialize_pattern,
    create_pattern,
    delete_pattern,
    get_event_by_uuid,
    get_pattern_by_uuid,
    list_active_patterns_grouped,
    list_patterns_admin,
    list_spam_events,
    mark_false_positive,
    spam_event_stats,
    update_pattern,
)

# =============================================================================
# Public read — source-key gated
# =============================================================================
public_router = APIRouter(
    prefix="/spam-patterns",
    tags=["spam-patterns"],
    dependencies=[Depends(require_api_key)],
)


@public_router.get("")
async def get_active_patterns_public(
    db: AsyncSession = Depends(get_db),
):
    """Return active patterns grouped by kind. Consumer sites fetch this at
    build/deploy time to keep their server-side filter in sync with Client
    Hub's canonical list."""
    return await list_active_patterns_grouped(db)


# =============================================================================
# Admin — root-key gated
# =============================================================================
admin_router = APIRouter(
    prefix="/admin",
    tags=["spam-admin"],
    dependencies=[Depends(require_root_key)],
)


# --------- patterns -----------------------------------------------------------
@admin_router.get("/spam-patterns")
async def admin_list_patterns(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    is_active: bool | None = None,
    pattern_kind: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await list_patterns_admin(
        db,
        page=page,
        per_page=per_page,
        is_active=is_active,
        pattern_kind=pattern_kind,
    )


@admin_router.post("/spam-patterns", status_code=201)
async def admin_create_pattern(
    body: SpamPatternCreate,
    ctx: SourceContext = Depends(require_root_key),
    db: AsyncSession = Depends(get_db),
):
    try:
        pattern = await create_pattern(
            db,
            {
                **body.model_dump(),
                "created_by": "root_admin" if ctx.is_root else f"source:{ctx.source_id}",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _serialize_pattern(pattern)


@admin_router.put("/spam-patterns/{uuid}")
async def admin_update_pattern(
    uuid: str,
    body: SpamPatternUpdate,
    db: AsyncSession = Depends(get_db),
):
    pattern = await get_pattern_by_uuid(db, uuid)
    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern {uuid} not found")
    try:
        pattern = await update_pattern(
            db, pattern, body.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _serialize_pattern(pattern)


@admin_router.delete("/spam-patterns/{uuid}", status_code=204)
async def admin_delete_pattern(
    uuid: str, db: AsyncSession = Depends(get_db)
):
    pattern = await get_pattern_by_uuid(db, uuid)
    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern {uuid} not found")
    await delete_pattern(db, pattern)


# --------- events -------------------------------------------------------------
@admin_router.get("/spam-events")
async def admin_list_events(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    endpoint: str | None = None,
    integration_kind: str | None = None,
    rejection_reason: str | None = None,
    submitted_email: str | None = None,
    was_false_positive: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await list_spam_events(
        db,
        page=page,
        per_page=per_page,
        endpoint=endpoint,
        integration_kind=integration_kind,
        rejection_reason=rejection_reason,
        submitted_email=submitted_email,
        was_false_positive=was_false_positive,
    )


@admin_router.get("/spam-events/stats")
async def admin_event_stats(db: AsyncSession = Depends(get_db)):
    return await spam_event_stats(db)


@admin_router.post("/spam-events/{uuid}/mark-false-positive")
async def admin_mark_event_false_positive(
    uuid: str, db: AsyncSession = Depends(get_db)
):
    event = await get_event_by_uuid(db, uuid)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {uuid} not found")
    event = await mark_false_positive(db, event)
    return {
        "uuid": event.uuid,
        "was_false_positive": bool(event.was_false_positive),
    }
