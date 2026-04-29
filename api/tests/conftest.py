import pymysql
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import get_db
from app.main import app

API_KEY = settings.api_key


@pytest.fixture(autouse=True, scope="session")
def _reset_spam_state():
    """Clear spam_rate_log + spam_events at session start.

    The rate-limit log persists between pytest runs by design (durable,
    multi-worker safe in production). In test, that means a clean-payload
    submission from a prior run can rate-limit the same submission in this
    run if both occur within the 10-min window. Wiping spam_rate_log +
    spam_events at session start gives every run a clean slate while
    leaving spam_patterns (the seeded library) intact.

    Sync (pymysql) on purpose: pytest-asyncio session-scope fixtures fight
    function-scope event loops; the cleanup is one-shot and trivial.
    """
    conn = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM spam_rate_log")
            cur.execute("DELETE FROM spam_events")
        conn.commit()
    finally:
        conn.close()
    yield


@pytest.fixture
def auth_headers():
    return {"X-API-Key": API_KEY}


@pytest_asyncio.fixture
async def client():
    # Create a fresh engine per test to avoid event loop conflicts
    test_engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with test_session() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await test_engine.dispose()
