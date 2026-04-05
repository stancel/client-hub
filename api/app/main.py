from fastapi import FastAPI

from app.routers import contacts, health, lookup

app = FastAPI(
    title="Client Hub API",
    description="Data-first customer intelligence microservice",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Health (no auth required)
app.include_router(health.router, prefix="/api/v1")

# Authenticated routes
app.include_router(lookup.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")
