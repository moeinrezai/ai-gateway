<div dir="rtl">

🚀 Enterprise AI Gateway

<div align="center">










یک AI Gateway امن، مقیاس‌پذیر و حرفه‌ای برای مدیریت متمرکز، امن و قابل‌کنترل درخواست‌های هوش مصنوعی

گزارش تست‌ها • مستندات API • دموی Rate Limiting

</div>

🎬 دمو ویدئویی

<p align="center">
  <img
    src="docs/swagger_ui/AI Gateway - Swagger UI - Google Chrome 9_6_2026 10_33_26 PM.png"
    alt="Rate Limiting Login Demo"
    width="900"
  />
</p>

<p align="center">
  <a href="https://aparat.com/v/kbkj2a6" target="_blank" rel="noopener noreferrer">
    <img
      src="https://img.shields.io/badge/▶-E53935?style=for-the-badge"
    />
  </a>
</p>

<p align="center">
  <strong>اجرای واقعی Rate Limiting در سناریوی Login تحت درخواست‌های متوالی</strong>
</p>

<p align="center">
  <sub>
    برای مشاهده اجرای کامل تست، روی دکمه بالا کلیک کنید؛ ویدئو در آپارات پخش می‌شود.
  </sub>
</p>

📋 فهرست مطالب

معرفی پروژه

نقشه معماری کامل

ویژگی‌های کلیدی

سیستم احراز هویت

مکانیزم Rate Limiting

ساختار پروژه

دستورات راه‌اندازی

مدیریت پکیج با uv

API Endpoints

تست‌ها و QA

امنیت

مستندات

🎯 معرفی پروژه

این پروژه یک AI Gateway حرفه‌ای است که به عنوان لایه میانی بین کلاینت و ارائه‌دهندگان سرویس‌های هوش مصنوعی (مانند OpenAI) قرار می‌گیرد. هدف اصلی این پروژه:

مدیریت متمرکز API Keyها: کلاینت هرگز به API Keyهای Providerها دسترسی ندارد

امنیت سطح Enterprise: پیاده‌سازی JWT، CSRF Protection، Rate Limiting و Session Management

مقیاس‌پذیری: معماری ماژولار برای اضافه کردن Providerهای جدید بدون تغییر در کد

Observability: Logging ساختاریافته و Request Tracking

🗺️ نقشه معماری کامل

نمای کلی سیستم

<div dir="ltr">


graph TB

    subgraph "Client Layer"

        Browser[Web Browser]

        Mobile[Mobile App]

        Postman[Postman/Testing]

    end

    subgraph "AI Gateway - FastAPI"

        subgraph "Middleware Stack"

            CORS[CORS Middleware]

            Proxy[Trusted Proxy<br/>IP Extraction]

            ReqID[Request ID<br/>Generator]

            CSRF[CSRF Protection<br/>Double Submit]

            RateLimit[Rate Limiter<br/>Redis-based]

        end

        subgraph "Authentication Layer"

            JWT[JWT Validation]

            Session[Session Manager]

            Cookie[Secure Cookie<br/>Handler]

        end

        subgraph "Authorization Layer"

            RBAC[RBAC Engine]

            Perm[Permission Checker]

        end

        subgraph "Business Logic"

            AuthService[Auth Service]

            UserService[User Service]

            SessionService[Session Service]

            AIService[AI Service]

        end

        subgraph "AI Provider Layer"

            ProviderFactory[Provider Factory]

            OpenAI[OpenAI Provider]

            Mock[Mock Provider]

        end

        subgraph "Data Layer"

            UserRepo[User Repository]

            SessionRepo[Session Repository]

            TokenRepo[Token Repository]

        end

    end

    subgraph "Storage Layer"

        PostgreSQL[(PostgreSQL<br/>Users, Sessions,<br/>Tokens, Roles)]

        Redis[(Redis<br/>Rate Limits,<br/>Token Denylist)]

    end

    subgraph "External Services"

        OpenAIAPI[OpenAI API]

    end

    Browser --> CORS

    Mobile --> CORS

    Postman --> CORS

    CORS --> Proxy

    Proxy --> ReqID

    ReqID --> CSRF

    CSRF --> RateLimit

    RateLimit --> JWT

    JWT --> Session

    Session --> Cookie

    Cookie --> RBAC

    RBAC --> Perm

    Perm --> AuthService

    Perm --> UserService

    Perm --> SessionService

    Perm --> AIService

    AuthService --> UserRepo

    UserService --> UserRepo

    SessionService --> SessionRepo

    SessionService --> TokenRepo

    AIService --> ProviderFactory

    ProviderFactory --> OpenAI

    ProviderFactory --> Mock

    UserRepo --> PostgreSQL

    SessionRepo --> PostgreSQL

    TokenRepo --> PostgreSQL

    RateLimit --> Redis

    OpenAI --> OpenAIAPI

    style AI_Gateway fill:#009688,stroke:#fff,stroke-width:3px,color:#fff

    style PostgreSQL fill:#336791,stroke:#fff,stroke-width:2px,color:#fff

    style Redis fill:#DC382D,stroke:#fff,stroke-width:2px,color:#fff


</div>

جریان درخواست (Request Flow)

<div dir="ltr">


sequenceDiagram

    participant C as Client

    participant M as Middleware Stack

    participant A as Auth Layer

    participant B as Business Logic

    participant AI as AI Provider

    participant DB as Database

    participant R as Redis

    C->>M: POST /api/v1/ai/chat

    M->>M: Extract Real IP (Trusted Proxy)

    M->>M: Generate Request ID

    M->>M: Validate CSRF Token

    M->>R: Check Rate Limit

    R-->>M: Allowed/Denied

    alt Rate Limit Exceeded

        M-->>C: 429 Too Many Requests

    else Rate Limit OK

        M->>A: Validate JWT Token

        A->>DB: Check Session Active

        DB-->>A: Session Status

        A->>A: Check Permissions

        A->>B: Forward Request

        B->>AI: Send Request to Provider

        AI-->>B: Provider Response

        B->>B: Normalize Response

        B-->>C: 200 OK with Response

    end


</div>

✨ ویژگی‌های کلیدی

🔐 امنیت و احراز هویت

JWT با چرخش امن: Access Token (۱۵ دقیقه) + Refresh Token (۷ روز) با Rotation

CSRF Protection: الگوی Double Submit Cookie برای جلوگیری از حملات CSRF

Secure Cookies: HttpOnly, Secure, SameSite=Lax برای تمام توکن‌ها

Session Management: ردیابی User-Agent، IP Hash، و قابلیت Revoke

Rate Limiting: محدودسازی نرخ درخواست بر اساس IP و User با Redis

🏗️ معماری

Clean Architecture: جداسازی Router, Service, Repository

Provider Abstraction: لایه انتزاعی برای اضافه کردن Providerهای جدید

Async First: استفاده بهینه از Async/Await در تمام لایه‌ها

Dependency Injection: مدیریت وابستگی‌ها با FastAPI DI

🐳 زیرساخت

Dockerized: محیط‌های Development, Testing, Production ایزوله

uv Package Manager: مدیریت سریع و مدرن وابستگی‌ها

Alembic Migrations: مدیریت نسخه‌بندی دیتابیس

Hot Reload: تغییرات کد بلافاصله اعمال می‌شوند (Development)

🔑 سیستم احراز هویت

انواع احراز هویت پیاده‌سازی شده

1. JWT Authentication (Access Token)

<div dir="ltr">


Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...


</div>

مدت اعتبار: ۱۵ دقیقه

الگوریتم: HS256

Claims: sub, sid, type, jti, iat, nbf, exp, role, csrf

ویژگی‌ها:

  - Stateless (بدون نیاز به Database برای Validation)

  - شامل Session ID برای ردیابی

  - شامل CSRF Token برای محافظت

2. Refresh Token

<div dir="ltr">


Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...


</div>

مدت اعتبار: ۷ روز

ذخیره‌سازی: Database (برای Revocation)

ویژگی‌ها:

  - Rotation: هر بار استفاده، توکن جدید صادر می‌شود

  - Replay Detection: استفاده مجدد از توکن قدیمی = Revoke کل Session

  - JTI: شناسه یکتا برای هر توکن

3. Session-Based Authentication

<div dir="ltr">


Cookie: access_token=...; refresh_token=...; csrf_token=...


</div>

Session Tracking:

  - User-Agent

  - IP Hash (SHA-256)

  - Created At

  - Last Used At

  - Is Active

4. CSRF Protection (Double Submit Cookie)

<div dir="ltr">


Cookie: csrf_token=abc123...

Header: X-CSRF-Token: abc123...


</div>

الگوریتم: UUID v4

مدت اعتبار: ۱ ساعت

ویژگی‌ها:

  - Cookie غیر HttpOnly (قابل خواندن توسط JavaScript)

  - Header در تمام درخواست‌های State-Changing (POST, PUT, DELETE)

  - مقایسه مقدار Cookie با Header

جریان کامل Login

<div dir="ltr">


sequenceDiagram

    participant C as Client

    participant API as FastAPI

    participant DB as PostgreSQL

    participant R as Redis

    C->>API: POST /api/v1/auth/login

    API->>R: Check Rate Limit (IP)

    R-->>API: Allowed

    API->>DB: Validate Credentials

    DB-->>API: User Found

    API->>DB: Create Session

    DB-->>API: Session ID

    API->>API: Generate Access Token (JWT)

    API->>API: Generate Refresh Token (JWT)

    API->>API: Generate CSRF Token (UUID)

    API->>DB: Store Refresh Token (JTI)

    DB-->>API: Token Stored

    API-->>C: Set-Cookie: access_token, refresh_token, csrf_token

    API-->>C: 200 OK with User Data


</div>

🚦 مکانیزم Rate Limiting

الگوریتم: Sliding Window Log

<div dir="ltr">


graph LR

    A[Request Arrives] --> B{Check Redis}

    B --> C[Get Request Timestamps]

    C --> D{Count in Window}

    D -->|> Limit| E[429 Too Many Requests]

    D -->|≤ Limit| F[Add Timestamp to Redis]

    F --> G[Process Request]

    G --> H[Return Response]


</div>

محدودیت‌های تعریف شده

<div dir="ltr">

| Endpoint | Limit | Window | Scope |

|----------|-------|--------|-------|

| /api/v1/auth/login | 5 | ۱ دقیقه | IP |

| /api/v1/auth/register | 3 | ۱ دقیقه | IP |

| /api/v1/ai/chat | 20 | ۱ دقیقه | IP + User |

| /api/v1/ai/generate | 10 | ۱ دقیقه | IP + User |

| سایر Endpoints | 100 | ۱ دقیقه | IP |

</div>

مثال عملی: Rate Limit در Login

سناریو: کاربر سعی می‌کند ۶ بار در ۱ دقیقه لاگین کند

<div dir="ltr">


# درخواست 1-5: موفق

POST /api/v1/auth/login

Response: 200 OK

# درخواست 6: مسدود شده

POST /api/v1/auth/login

Response: 429 Too Many Requests

{

  "success": false,

  "error": {

    "code": "RATE_LIMIT_EXCEEDED",

    "message": "Too many login attempts. Please try again later.",

    "details": {

      "limit": 5,

      "window": "1 minute",

      "retry_after": 45

    }

  }

}


</div>

📺 **مشاهده ویدئوی دمو: Rate Limiting در عمل

📁 ساختار پروژه

<div dir="ltr">


ai-gateway/

├── app/                          # کد اصلی برنامه

│   ├── api/                      # لایه API

│   │   ├── dependencies/         # FastAPI Dependencies

│   │   │   ├── auth.py           # Authentication Dependencies

│   │   │   ├── db.py             # Database Session

│   │   │   ├── rate_limit.py     # Rate Limiting

│   │   │   └── services.py       # Service Injection

│   │   ├── middleware/           # Middlewareها

│   │   │   ├── csrf.py           # CSRF Protection

│   │   │   ├── request_id.py     # Request ID Generator

│   │   │   └── trusted_proxy.py  # IP Extraction

│   │   └── v1/                   # API Version 1

│   │       ├── routers/          # Endpoint Routers

│   │       │   ├── auth.py       # Authentication Endpoints

│   │       │   ├── users.py      # User Endpoints

│   │       │   ├── sessions.py   # Session Endpoints

│   │       │   └── ai.py         # AI Endpoints

│   │       └── router.py         # Main Router

│   │

│   ├── core/                     # هسته برنامه

│   │   ├── config/               # Configuration

│   │   │   └── settings.py       # Pydantic Settings

│   │   ├── security/             # Security Utilities

│   │   │   ├── jwt.py            # JWT Operations

│   │   │   ├── password.py       # Password Hashing

│   │   │   └── csrf.py           # CSRF Token

│   │   ├── exceptions/           # Custom Exceptions

│   │   │   ├── auth.py           # Auth Exceptions

│   │   │   ├── ai.py             # AI Exceptions

│   │   │   └── rate_limit.py     # Rate Limit Exceptions

│   │   ├── logging/              # Logging Configuration

│   │   │   └── config.py         # Structured Logging

│   │   └── redis/                # Redis Client

│   │       └── client.py         # Redis Connection

│   │

│   ├── models/                   # SQLAlchemy Models

│   │   ├── user.py               # User Model

│   │   ├── session.py            # Session Model

│   │   ├── refresh_token.py      # Refresh Token Model

│   │   ├── role.py               # Role Model

│   │   └── permission.py         # Permission Model

│   │

│   ├── schemas/                  # Pydantic Schemas

│   │   ├── auth.py               # Auth Schemas

│   │   ├── user.py               # User Schemas

│   │   ├── session.py            # Session Schemas

│   │   └── ai.py                 # AI Schemas

│   │

│   ├── repositories/             # Data Access Layer

│   │   ├── base.py               # Base Repository

│   │   ├── user.py               # User Repository

│   │   ├── session.py            # Session Repository

│   │   └── refresh_token.py      # Token Repository

│   │

│   ├── services/                 # Business Logic Layer

│   │   ├── auth.py               # Auth Service

│   │   ├── user.py               # User Service

│   │   ├── session.py            # Session Service

│   │   └── ai.py                 # AI Service

│   │

│   ├── ai/                       # AI Provider Layer

│   │   ├── providers/            # Provider Implementations

│   │   │   ├── base.py           # Base Provider Interface

│   │   │   ├── openai.py         # OpenAI Provider

│   │   │   └── mock.py           # Mock Provider (Testing)

│   │   ├── factory.py            # Provider Factory

│   │   └── schemas.py            # AI Schemas

│   │

│   └── main.py                   # FastAPI Application

│

├── alembic/                      # Database Migrations

│   ├── versions/                 # Migration Files

│   └── env.py                    # Alembic Environment

│

├── scripts/                      # Utility Scripts

│   └── seed_roles.py             # Seed Initial Roles

│

├── tests/                        # Test Suite

│   ├── conftest.py               # Pytest Fixtures

│   ├── test_auth.py              # Auth Tests

│   ├── test_session.py           # Session Tests

│   └── test_ai.py                # AI Tests

│

├── docs/                         # Documentation

│   ├── test_results/             # Test Reports

│   └── screenshots/              # Screenshots

│

├── docker/                       # Docker Configuration

│   ├── Dockerfile                # Backend Dockerfile

│   ├── docker-compose.yml        # Main Compose

│   └── docker-compose.override.yml # Dev Overrides

│

├── .env                          # Environment Variables (Not in Git)

├── .env.example                  # Example Environment

├── pyproject.toml                # Python Project Config

├── uv.lock                       # uv Lock File

├── alembic.ini                   # Alembic Config

└── README.md                     # This File


</div>

🚀 دستورات راه‌اندازی

پیش‌نیازها

Docker Desktop (ویندوز)

uv (مدیریت پکیج پایتون)

PowerShell

۱. کلون کردن پروژه

<div dir="ltr">


git clone https://github.com/moeinrezai/ai-gateway.git

cd ai-gateway


</div>

۲. نصب وابستگی‌ها با uv

<div dir="ltr">


# نصب uv (اگر نصب نیست)

pip install uv

# همگام‌سازی وابستگی‌ها

uv sync


</div>

۳. تنظیم Environment Variables

<div dir="ltr">


# کپی فایل نمونه

Copy-Item .env.example .env

# ویرایش فایل .env و تنظیم مقادیر

notepad .env


</div>

مقادیر ضروری در .env:

<div dir="ltr">


# Database

DB_HOST=localhost

DB_PORT=5432

DB_USER=postgres

DB_PASSWORD=your_secure_password

DB_NAME=ai_gateway

# Redis

REDIS_HOST=localhost

REDIS_PORT=6379

# Security

JWT_SECRET_KEY=your_super_secret_key_here

CSRF_ENABLED=true

CSRF_COOKIE_SECURE=false  # در Development

# AI Provider

OPENAI_API_KEY=sk-your-openai-api-key


</div>

۴. راه‌اندازی با Docker Compose

<div dir="ltr">


# Build و اجرای سرویس‌ها

docker-compose -f docker/docker-compose.yml up -d --build

# بررسی وضعیت کانتینرها

docker-compose -f docker/docker-compose.yml ps


</div>

۵. اعمال Migrationهای دیتابیس

<div dir="ltr">


# ساخت جداول

docker-compose -f docker/docker-compose.yml exec backend uv run alembic upgrade head

# Seed کردن Roleهای اولیه

docker-compose -f docker/docker-compose.yml exec backend uv run python scripts/seed_roles.py


</div>

۶. دسترسی به سرویس‌ها

API: http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

دستورات پرکاربرد

<div dir="ltr">


# مشاهده لاگ‌ها

docker-compose -f docker/docker-compose.yml logs -f backend

# ری‌استارت Backend

docker-compose -f docker/docker-compose.yml restart backend

# ورود به Shell کانتینر

docker-compose -f docker/docker-compose.yml exec backend bash

# اجرای تست‌ها

docker-compose -f docker/docker-compose.yml exec backend uv run pytest -v

# توقف سرویس‌ها

docker-compose -f docker/docker-compose.yml down

# توقف و پاکسازی Volumeها (هشدار: داده‌ها پاک می‌شوند)

docker-compose -f docker/docker-compose.yml down -v


</div>

📦 مدیریت پکیج با uv

چرا uv؟

سرعت: ۱۰-۱۰۰x سریع‌تر از pip

قابلیت اطمینان: Lock File برای Reproducible Builds

مدرن: پشتیبانی از Pyproject.toml

سازگاری: کاملاً compatible با PyPI

دستورات uv

<div dir="ltr">


# همگام‌سازی وابستگی‌ها از pyproject.toml

uv sync

# اضافه کردن پکیج جدید

uv add <package-name>

# حذف پکیج

uv remove <package-name>

# به‌روزرسانی پکیج‌ها

uv lock --upgrade

# اجرای دستور در محیط مجازی

uv run <command>

# مثال: اجرای pytest

uv run pytest -v

# مثال: اجرای alembic

uv run alembic upgrade head


</div>

فایل‌های مرتبط

pyproject.toml: تعریف وابستگی‌ها و تنظیمات پروژه

uv.lock: Lock File برای نسخه‌های دقیق پکیج‌ها

📡 API Endpoints

Authentication

<div dir="ltr">

| Method | Endpoint | Description | Auth Required | CSRF Required |

|--------|----------|-------------|---------------|---------------|

| POST | /api/v1/auth/register | ثبت‌نام کاربر جدید | ❌ | ❌ |

| POST | /api/v1/auth/login | ورود کاربر | ❌ | ❌ |

| POST | /api/v1/auth/logout | خروج از حساب | ✅ | ✅ |

| POST | /api/v1/auth/refresh | نوسازی توکن‌ها | ✅ (Refresh Token) | ✅ |

| POST | /api/v1/auth/change-password | تغییر رمز عبور | ✅ | ✅ |

</div>

Users

<div dir="ltr">

| Method | Endpoint | Description | Auth Required | CSRF Required |

|--------|----------|-------------|---------------|---------------|

| GET | /api/v1/users/me | دریافت پروفایل کاربر فعلی | ✅ | ❌ |

| GET | /api/v1/users/admin-only | تست دسترسی Admin | ✅ (Admin) | ❌ |

</div>

Sessions

<div dir="ltr">

| Method | Endpoint | Description | Auth Required | CSRF Required |

|--------|----------|-------------|---------------|---------------|

| GET | /api/v1/sessions/ | لیست Sessionهای فعال | ✅ | ❌ |

| DELETE | /api/v1/sessions/{id} | لغو یک Session خاص | ✅ | ✅ |

| DELETE | /api/v1/sessions/ | لغو تمام Sessionها | ✅ | ✅ |

</div>

AI

<div dir="ltr">

| Method | Endpoint | Description | Auth Required | CSRF Required |

|--------|----------|-------------|---------------|---------------|

| POST | /api/v1/ai/chat | چت با AI | ✅ | ✅ |

| POST | /api/v1/ai/generate | تولید متن با AI | ✅ | ✅ |

</div>

Health

<div dir="ltr">

| Method | Endpoint | Description | Auth Required |

|--------|----------|-------------|---------------|

| GET | /health | بررسی سلامت سرویس | ❌ |

</div>

🧪 تست‌ها و QA

اجرای تست‌ها

<div dir="ltr">


# اجرای تمام تست‌ها

docker-compose -f docker/docker-compose.yml exec backend uv run pytest -v

# اجرای تست‌های خاص

docker-compose -f docker/docker-compose.yml exec backend uv run pytest tests/test_auth.py -v

# اجرای تست‌ها با Coverage

docker-compose -f docker/docker-compose.yml exec backend uv run pytest --cov=app -v


</div>

گزارش تست‌ها

📊 مشاهده گزارش کامل تست‌های پاس شده

✅ test_auth.py: ۴ تست پاس شده

✅ test_session.py: ۳ تست پاس شده

✅ test_ai.py: ۳ تست پاس شده

انواع تست‌ها

۱. Unit Tests: تست توابع مستقل

۲. Integration Tests: تست یکپارچگی لایه‌ها

۳. Security Tests: تست مکانیزم‌های امنیتی

۴. API Tests: تست Endpointها

🔒 امنیت

ویژگی‌های امنیتی پیاده‌سازی شده

✅ JWT Authentication: با Access/Refresh Token

✅ CSRF Protection: Double Submit Cookie Pattern

✅ Secure Cookies: HttpOnly, Secure, SameSite

✅ Rate Limiting: IP-based و User-based

✅ Session Management: ردیابی و Revoke

✅ Password Hashing: Argon2id

✅ Input Validation: Pydantic Schemas

✅ SQL Injection Protection: SQLAlchemy ORM

✅ XSS Protection: HttpOnly Cookies

✅ Request ID Tracking: برای Observability

Threat Model

📄 مشاهده مستندات کامل امنیت

📚 مستندات

📖 مستندات API (Swagger)

🏗️ معماری سیستم

🔐 راهنمای امنیت

🧪 گزارش تست‌ها

🎥 دموی Rate Limiting

📌 وضعیت پروژه

این مخزن یک نمونه عملی از طراحی یک AI Gateway با تمرکز بر امنیت، کنترل دسترسی، مدیریت Session، Rate Limiting، جداسازی لایه‌ها و قابلیت اتصال به Providerهای هوش مصنوعی است.

Demo: برای مشاهده سناریوی عملی Rate Limiting، به بخش دموی Rate Limiting مراجعه کنید.

🤝 مشارکت

ما از مشارکت جامعه متن‌باز استقبال می‌کنیم! لطفاً قبل از ارسال Pull Request:

۱. یک Issue باز کنید

۲. از Conventional Commits استفاده کنید

۳. تست‌ها را اجرا کنید

۴. Documentation را به‌روزرسانی کنید

📄 مجوز

این پروژه تحت مجوز MIT License منتشر شده است.

<div align="center">

</div>

</div>