<div dir="rtl">🧪 گزارش تست‌ها — AI Gateway
این سند خلاصه و جزئیات اجرای تست‌های پروژه AI Gateway را بر اساس خروجی واقعی اجرای pytest در محیط Docker ارائه می‌کند.
</div><div dir="ltr">
Last Updated: 2026-10-31
Test Framework: pytest 9.1.1 + pytest-asyncio 1.4.2
Python: 3.12.16
Environment: Docker (Linux Container)
Command: uv run pytest
Status: ✅ ALL EXECUTED TESTS PASSING (1 test skipped)
</div><div dir="rtl">📊 خلاصه وضعیت تست‌ها
</div><div dir="ltr">Metric	Value
Collected Tests	89
Passed	88 ✅
Failed	0 ❌
Skipped	1 ⏭️
Success Rate	100% of executed tests
Test Duration	39.87 seconds
Warnings	2 deprecation warnings
Coverage Areas	AI, Authentication, Authorization, Cookies, CSRF, Error Handling, Passwords, Rate Limiting, Sessions


</div><div dir="rtl">توضیح: از ۸۹ تست جمع‌آوری‌شده، ۸۸ تست پاس شده و یک تست با وضعیت Skipped اجرا نشده است. هیچ تستی Fail نشده. نرخ موفقیت ۱۰۰٪ بر اساس تست‌های اجراشده محاسبه شده است.

</div><div dir="rtl">🎯 نتایج به تفکیک دسته‌بندی
</div><div dir="ltr">Test File	Category	Passed	Skipped	Failed	Result
tests/test_ai.py	AI Provider	3	1	0	✅ PASS
tests/test_ai_errors.py	AI Error Handling	12	0	0	✅ PASS
tests/test_auth.py	Authentication	4	0	0	✅ PASS
tests/test_auth_flow.py	Authentication Flow	14	0	0	✅ PASS
tests/test_authorization.py	Authorization	6	0	0	✅ PASS
tests/test_cookie_security.py	Cookie Security	11	0	0	✅ PASS
tests/test_csrf.py	CSRF Protection	4	0	0	✅ PASS
tests/test_error_handling.py	General Error Handling	12	0	0	✅ PASS
tests/test_password.py	Password Security	6	0	0	✅ PASS
tests/test_rate_limit.py	Rate Limiting	4	0	0	✅ PASS
tests/test_session.py	Session Management	3	0	0	✅ PASS
tests/test_session_advanced.py	Advanced Session Management	9	0	0	✅ PASS
Total		88	1	0	✅ PASS


</div><div dir="rtl">🧩 حوزه‌های پوشش داده‌شده
- AI Provider: تست‌های مسیر موفق و اعتبارسنجی درخواست‌های AI
- AI Error Handling: مدیریت خطاهای مرتبط با سرویس AI
- Authentication & Auth Flow: ثبت‌نام، ورود، دسترسی به پروفایل و جریان‌های احراز هویت
- Authorization: کنترل دسترسی و مجوزها
- Cookie Security: تنظیمات و امنیت کوکی‌ها
- CSRF Protection: محافظت در برابر درخواست‌های جعل‌شده
- Error Handling: رفتار API در شرایط خطا
- Password Security: اعتبارسنجی و سناریوهای امنیتی رمز عبور
- Rate Limiting: محدودسازی تعداد درخواست‌ها
- Session Management: مدیریت نشست، نوسازی توکن و سناریوهای پیشرفته نشست
</div><div dir="rtl">🖥️ خروجی اجرای تست‌ها
</div>platform linux -- Python 3.12.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /app
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.2, locust-2.46.4, asyncio-1.4.0, Faker-40.37.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 89 items

tests/test_ai.py .s..                         [  4%]
tests/test_ai_errors.py ............           [ 17%]
tests/test_auth.py ....                        [ 22%]
tests/test_auth_flow.py ..............         [ 38%]
tests/test_authorization.py ......             [ 44%]
tests/test_cookie_security.py ...........       [ 57%]
tests/test_csrf.py ....                        [ 61%]
tests/test_error_handling.py ............       [ 75%]
tests/test_password.py ......                   [ 82%]
tests/test_rate_limit.py ....                  [ 86%]
tests/test_session.py ...                      [ 89%]
tests/test_session_advanced.py .........        [100%]

88 passed, 1 skipped, 2 warnings in 39.87s
<div dir="rtl">⚠️ هشدارهای اجرای تست
در این اجرا، دو DeprecationWarning از کتابخانه httpx گزارش شده است. هشدارها در دو تست زیر ظاهر شده‌اند:
</div>tests/test_auth_flow.py::test_refresh_rotation_revoked_old_token_and_session
tests/test_session.py::test_refresh_token_replay_attack
<div dir="rtl">علت هشدار: استفاده از پارامتر cookies در سطح یک درخواست، رفتاری است که در نسخه‌های آینده httpx حذف خواهد شد؛ زیرا مدیریت ماندگاری کوکی‌ها در سطح درخواست می‌تواند مبهم باشد.

پیشنهاد اصلاح: در صورت نیاز به رفع هشدار، کوکی‌ها از طریق خود AsyncClient تنظیم شوند، نه به‌صورت per-request.

این هشدارها مانع موفقیت تست‌ها نشده‌اند؛ هر دو تست مربوطه پاس شده‌اند.
</div><div dir="rtl">▶️ اجرای تست‌ها
پیش‌نیازها
- Docker Desktop در حال اجرا باشد.
- کانتینر backend فعال باشد.
- وابستگی‌های پروژه با uv نصب شده باشند.
- تنظیمات محیط تست و دیتابیس مطابق پروژه آماده باشند.
اجرای تمام تست‌ها
</div>uv run pytest
<div dir="rtl">اجرای تست‌ها با جزئیات بیشتر
</div>uv run pytest -v
<div dir="rtl">اجرای یک فایل تست مشخص
</div>uv run pytest tests/test_auth.py -v
uv run pytest tests/test_session.py -v
uv run pytest tests/test_ai.py -v
<div dir="rtl">اجرای تست‌ها داخل کانتینر Docker
</div>docker exec -it <backend-container> bash
uv run pytest
<div dir="rtl">نام کانتینر را با نام واقعی سرویس backend در محیط خود جایگزین کنید.

</div><div dir="rtl">🍪 راهنمای CSRF در Postman
چرا CSRF Token لازم است؟
AI Gateway از الگوی Double Submit Cookie برای محافظت CSRF استفاده می‌کند:
1. سرور هنگام ورود، کوکی csrf_token را تنظیم می‌کند.
2. کلاینت مقدار کوکی را می‌خواند.
3. کلاینت مقدار را در هدر X-CSRF-Token ارسال می‌کند.
4. سرور مقدار هدر و کوکی را اعتبارسنجی می‌کند.
درخواست‌های تغییردهنده وضعیت که فاقد CSRF معتبر باشند، باید با 403 Forbidden رد شوند.
تنظیم دستی
1. ابتدا به endpoint ورود درخواست بفرستید.
2. از بخش Cookies مقدار csrf_token را بردارید.
3. در درخواست محافظت‌شده، هدر زیر را اضافه کنید:
</div>X-CSRF-Token: <csrf_token_value>
<div dir="rtl">Endpointهای مرتبط
</div><div dir="ltr">Endpoint	Method	CSRF
/api/v1/auth/register	POST	Not required
/api/v1/auth/login	POST	Not required
/api/v1/auth/logout	POST	Required
/api/v1/auth/refresh	POST	Required
/api/v1/auth/change-password	POST	Required
/api/v1/ai/chat	POST	Required
/api/v1/ai/generate	POST	Required
/api/v1/sessions/{id}	DELETE	Required
/api/v1/users/me	GET	Not required


</div><div dir="rtl">این جدول بر اساس ساختار مستند قبلی پروژه حفظ شده است؛ برای تغییرات احتمالی endpointها، آن را با تنظیمات فعلی API تطبیق دهید.

</div><div dir="rtl">🔍 تحلیل پوشش تست‌ها
مواردی که در مجموعه تست فعلی بررسی می‌شوند
- احراز هویت و جریان‌های ورود/ثبت‌نام
- کنترل دسترسی و مجوزها
- امنیت کوکی‌ها و CSRF
- مدیریت خطاهای API و خطاهای AI
- اعتبارسنجی رمز عبور
- Rate Limiting
- مدیریت نشست و چرخش/ابطال توکن
مواردی که از خروجی فعلی قابل تأیید نیستند
خروجی ارائه‌شده فقط نتیجه اجرای تست‌ها را نشان می‌دهد و شامل گزارش code coverage یا تست بار نیست. بنابراین موارد زیر از این خروجی قابل نتیجه‌گیری نیستند:
- درصد پوشش خطوط و شاخه‌های کد (Code Coverage)
- رفتار تحت بار بالا و تعداد درخواست‌های هم‌زمان
- عملکرد در شرایط timeout یا اختلال شبکه واقعی
- نتیجه تست‌های end-to-end خارج از مجموعه تست اجراشده
</div><div dir="rtl">🧪 زیرساخت تست
اطلاعات مشاهده‌شده در خروجی
- محیط اجرا: Linux داخل Docker
- Python: 3.12.16
- pytest: 9.1.1
- pytest-asyncio: 1.4.2
- حالت asyncio: AUTO
- مسیر تست‌ها: tests
نکته درباره تست Skipped
یک تست در tests/test_ai.py با وضعیت Skipped اجرا نشده است. خروجی فعلی دلیل skip شدن آن را نمایش نمی‌دهد؛ برای مشخص شدن علت باید تست با گزینه -rs اجرا شود:
</div>uv run pytest -rs
<div dir="rtl">✅ جمع‌بندی
در اجرای فعلی تست‌های AI Gateway:
- ۸۹ تست جمع‌آوری شدند.
- ۸۸ تست پاس شدند.
- ۱ تست Skip شد.
- هیچ تستی Fail نشد.
- نرخ موفقیت تست‌های اجراشده ۱۰۰٪ است.
- دو هشدار deprecation از httpx ثبت شد که مانع پاس شدن تست‌ها نبودند.
- زمان اجرای کل مجموعه تست‌ها ۳۹٫۸۷ ثانیه بود.
این نتیجه نشان می‌دهد مجموعه تست فعلی در مسیرهای پوشش‌داده‌شده، بدون شکست اجرا شده است. با این حال، برای ارزیابی کامل کیفیت و آمادگی انتشار، گزارش Code Coverage و تست‌های عملکردی نیز باید جداگانه بررسی شوند.
</div><div dir="ltr">Test Report Generated: 2026-10-31
Execution Result: 88 passed, 1 skipped, 0 failed
Duration: 39.87s
</div>