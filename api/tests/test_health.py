import pytest


@pytest.mark.asyncio
async def test_health_check_returns_ok(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_no_auth_required(client):
    # Health endpoint should work without API key
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
