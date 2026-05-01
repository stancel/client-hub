from pathlib import Path

from fastapi import FastAPI

from app.routers import (
    admin,
    affiliations,
    communications,
    contacts,
    health,
    invoices,
    lookup,
    marketing_sources,
    orders,
    organizations,
    settings,
    spam,
    webhooks,
)


def _read_version() -> str:
    """Single source of truth for the Client Hub API version.

    The ``VERSION`` file at the api/ project root is read at import time
    and exposed via the FastAPI ``/openapi.json`` and ``/docs`` UIs. The
    same file is consumed by ``scripts/generate-sdks.sh`` so SDK package
    versions move in lockstep, and by the release flow which tags
    ``vX.Y.Z`` at the corresponding commit.
    """
    version_path = Path(__file__).resolve().parent.parent / "VERSION"
    try:
        return version_path.read_text(encoding="utf-8").strip() or "0.0.0"
    except FileNotFoundError:
        return "0.0.0"


__version__ = _read_version()


app = FastAPI(
    title="Client Hub API",
    description="Data-first customer intelligence microservice",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Health (no auth required)
app.include_router(health.router, prefix="/api/v1")

# Authenticated routes
app.include_router(lookup.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")
app.include_router(affiliations.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(invoices.router, prefix="/api/v1")
app.include_router(communications.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(spam.public_router, prefix="/api/v1")
app.include_router(spam.admin_router, prefix="/api/v1")
app.include_router(marketing_sources.public_router, prefix="/api/v1")
