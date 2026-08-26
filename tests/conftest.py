import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.main import app
from app.api.dependencies.db import get_db
from app.core.config import settings
from app.core.security.password import hash_password
from app.models.user import User
from app.models.role import Role


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
def override_get_db(db_session):
    async def _get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    result = await db_session.execute(select(Role).where(Role.name == "user"))
    role = result.scalars().first()
    
    email = f"test_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        hashed_password=hash_password("SecurePass123!"),
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user