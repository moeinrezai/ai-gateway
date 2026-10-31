import pytest
import pytest_asyncio
import httpx
import redis.asyncio as aioredis
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.main import app
from app.api.dependencies.db import get_db
from app.core.redis import get_redis
from app.core.config.settings import settings
from app.core.security.password import hash_password
from app.models.user import User
from app.models.role import Role

fake = Faker()


@pytest_asyncio.fixture(scope="function")
async def flush_redis():
    test_redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await test_redis.flushdb()
    yield
    await test_redis.flushdb()
    await test_redis.aclose()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def override_get_db(db_session):
    async def _get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def override_get_redis():
    test_redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    
    async def _get_redis():
        yield test_redis
        
    app.dependency_overrides[get_redis] = _get_redis
    yield
    app.dependency_overrides.clear()
    await test_redis.aclose()


@pytest_asyncio.fixture(scope="function")
async def client(override_get_db, override_get_redis, flush_redis):
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def user_role(db_session):
    result = await db_session.execute(select(Role).where(Role.name == "user"))
    role = result.scalars().first()
    if not role:
        role = Role(name="user", description="Default user role")
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
    return role


@pytest_asyncio.fixture(scope="function")
async def admin_role(db_session):
    result = await db_session.execute(select(Role).where(Role.name == "admin"))
    role = result.scalars().first()
    if not role:
        role = Role(name="admin", description="Administrator role")
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
    return role


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session, user_role):
    email = fake.email()
    password = "SecurePass123!"
    
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role_id=user_role.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    user.password = password
    return user


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session, admin_role):
    email = fake.email()
    password = "AdminPass123!"
    
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role_id=admin_role.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    user.password = password
    return user


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(client: AsyncClient, test_user):
    login_payload = {
        "email": test_user.email,
        "password": test_user.password
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to authenticate test user: {response.status_code} - {response.text}"
        )
    
    client.cookies.update(response.cookies)
    
    csrf_token = response.cookies.get(settings.CSRF_COOKIE_NAME)
    if csrf_token:
        client.headers[settings.CSRF_HEADER_NAME] = csrf_token
    
    return client


@pytest_asyncio.fixture(scope="function")
async def admin_client(client: AsyncClient, admin_user):
    login_payload = {
        "email": admin_user.email,
        "password": admin_user.password
    }
    response = await client.post(
        f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload
    )
    
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to authenticate admin user: {response.status_code} - {response.text}"
        )
    
    client.cookies.update(response.cookies)
    
    csrf_token = response.cookies.get(settings.CSRF_COOKIE_NAME)
    if csrf_token:
        client.headers[settings.CSRF_HEADER_NAME] = csrf_token
    
    return client