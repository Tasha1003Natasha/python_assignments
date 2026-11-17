import asyncio
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.entity.models import Base, Contact, User
from src.database.db import get_db
from src.services.auth import auth_service
from src.services.rate_limiter import RateLimiter

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DATABASE_PATH = BASE_DIR / "test.db"
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DATABASE_PATH}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "deadpool",
             "email": "deadpool@example.com", "password": "12345678"}


@pytest.fixture(scope="session", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            await session.execute(delete(Contact))
            await session.execute(delete(User))
            hash_password = auth_service.get_password_hash(
                test_user["password"])
            current_user = User(username=test_user["username"], email=test_user["email"], password=hash_password,
                                avatar="https://example.com/avatar.png", confirmed=True, role="admin")
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest.fixture(autouse=True)
def mock_rate_limiter():
    class MockRateLimitCache:
        async def incr(self, key):
            return 1

        async def expire(self, key, seconds):
            return True

    def patch_dependencies(routes):
        for route in routes:
            patch_dependencies(getattr(route, "routes", []))
            original_router = getattr(route, "original_router", None)
            if original_router is not None:
                patch_dependencies(original_router.routes)

            dependant = getattr(route, "dependant", None)
            if dependant is None:
                continue
            for dependency in dependant.dependencies:
                call = dependency.call
                if isinstance(call, RateLimiter):
                    call.cache = MockRateLimitCache()

    patch_dependencies(app.routes)
