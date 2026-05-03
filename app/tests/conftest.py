import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import async_session, init_db
from app.auth import create_user


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    """Use an in-memory SQLite DB and seed an admin user for every test."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    import app.database as db_module
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.database import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session_local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # patch the module-level engine/session so app code uses them
    db_module.engine = engine
    db_module.async_session = async_session_local

    async def _get_db():
        async with async_session_local() as session:
            yield session

    db_module.get_db = _get_db

    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_session_local() as session:
            await create_user(session, "admin", "Demo0523", "Admin")
            await session.commit()

    import asyncio
    asyncio.get_event_loop().run_until_complete(_init())

    yield

    asyncio.get_event_loop().run_until_complete(engine.dispose())
