import uuid
import pytest
import pytest_asyncio
import httpx
import redis.asyncio as redis
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
from app.models.session import Session

fake = Faker()


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
    test_redis = redis.from_url(settings.redis_url, decode_responses=True)
    
    async def _get_redis():
        yield test_redis
        
    app.dependency_overrides[get_redis] = _get_redis
    yield
    app.dependency_overrides.clear()
    await test_redis.aclose()


@pytest_asyncio.fixture(scope="function")
async def client(override_get_db, override_get_redis):
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
async def authenticated_client(client: AsyncClient, test_user):
    login_payload = {
        "email": test_user.email,
        "password": test_user.password
    }
    response = await client.post(f"{settings.APP_API_V1_PREFIX}/auth/login", json=login_payload)
    
    if response.status_code != 200:
        raise RuntimeError(f"Failed to authenticate test user: {response.status_code} - {response.text}")
    
    # 1. به‌روزرسانی کوکی‌های کلاینت
    client.cookies.update(response.cookies)
    
    # 2. عیب‌یابی: چاپ اطلاعات دریافتی برای اطمینان از ارسال کوکی توسط بک‌اند
    print("\n=== LOGIN RESPONSE DEBUG ===")
    print(f"Cookies received by httpx: {list(response.cookies.keys())}")
    print(f"Raw Set-Cookie header: {response.headers.get('set-cookie')}")
    print(f"Expected CSRF Cookie Name: {settings.CSRF_COOKIE_NAME}")
    print("============================\n")
    
    # 3. تلاش برای دریافت توکن از object کوکی httpx
    csrf_token = response.cookies.get(settings.CSRF_COOKIE_NAME)
    
    # 4. اگر نبود، تلاش برای استخراج دستی از هدر Set-Cookie
    if not csrf_token:
        import re
        set_cookie_header = response.headers.get("set-cookie", "")
        match = re.search(rf'{settings.CSRF_COOKIE_NAME}=([^;]+)', set_cookie_header)
        if match:
            csrf_token = match.group(1)
            print(f"✅ Found CSRF token manually in Set-Cookie header: {csrf_token}")
        else:
            raise RuntimeError(
                f"❌ CRITICAL: Backend did NOT set the '{settings.CSRF_COOKIE_NAME}' cookie! "
                f"Available cookies: {list(response.cookies.keys())}. "
                f"Please check app/api/v1/routers/auth.py to ensure _set_auth_cookies includes csrf_token."
            )
            
    # 5. تنظیم هدر برای تمام درخواست‌های بعدی این کلاینت
    client.headers[settings.CSRF_HEADER_NAME] = csrf_token
    print(f"✅ Successfully set {settings.CSRF_HEADER_NAME} header for subsequent requests.\n")
    
    return client