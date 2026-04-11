from dataclasses import dataclass

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.api_key import ApiKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@dataclass
class SourceContext:
    """Resolved from the X-API-Key header on each request."""
    source_id: int | None  # None = root admin key
    is_root: bool


async def resolve_source_context(
    key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> SourceContext:
    """Resolve X-API-Key to a SourceContext. Checks root key first, then api_keys table."""
    if not key:
        raise HTTPException(status_code=401, detail="Missing API key")

    # Check root key (legacy API_KEY or new CLIENTHUB_ROOT_API_KEY)
    root_key = settings.clienthub_root_api_key or settings.api_key
    if key == root_key:
        return SourceContext(source_id=None, is_root=True)

    # Look up in api_keys table
    stmt = select(ApiKey).where(
        ApiKey.key_value == key,
        ApiKey.is_active == True,  # noqa: E712
        ApiKey.revoked_at.is_(None),
    )
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()

    if not api_key:
        # Fall back to legacy single API_KEY for backward compat in dev
        if key == settings.api_key:
            return SourceContext(source_id=None, is_root=True)
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")

    # Fire-and-forget update of last_used_at
    await db.execute(
        update(ApiKey).where(ApiKey.id == api_key.id).values(last_used_at=None)  # Will use DB CURRENT_TIMESTAMP
    )

    return SourceContext(source_id=api_key.source_id, is_root=False)


async def require_api_key(ctx: SourceContext = Depends(resolve_source_context)) -> SourceContext:
    """Standard auth dependency — any valid key (source or root)."""
    return ctx


async def require_root_key(ctx: SourceContext = Depends(resolve_source_context)) -> SourceContext:
    """Admin auth dependency — root key only."""
    if not ctx.is_root:
        raise HTTPException(status_code=403, detail="This endpoint requires the root admin API key")
    return ctx
