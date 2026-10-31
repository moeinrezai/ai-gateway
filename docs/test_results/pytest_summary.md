================================================================================
AI GATEWAY - TEST EXECUTION SUMMARY
================================================================================
Date: 2026-10-31
Environment: Docker (Linux Container)
Python: 3.12.16
Framework: pytest 9.1.1 + pytest-asyncio 1.4.2
Command: uv run pytest
Status: ALL EXECUTED TESTS PASSING (1 skipped)

================================================================================
TEST RESULTS OVERVIEW
================================================================================
Collected:       89
Passed:          88
Failed:          0
Skipped:         1
Success Rate:    100% of executed tests
Duration:        39.87 seconds
Warnings:        2 DeprecationWarnings (httpx)

================================================================================
DETAILED RESULTS BY FILE
================================================================================
tests/test_ai.py                 3 passed, 1 skipped
tests/test_ai_errors.py         12 passed
tests/test_auth.py               4 passed
tests/test_auth_flow.py         14 passed
tests/test_authorization.py      6 passed
tests/test_cookie_security.py   11 passed
tests/test_csrf.py               4 passed
tests/test_error_handling.py    12 passed
tests/test_password.py           6 passed
tests/test_rate_limit.py         4 passed
tests/test_session.py            3 passed
tests/test_session_advanced.py   9 passed

TOTAL                            88 passed, 1 skipped, 0 failed

================================================================================
WARNINGS
================================================================================
DeprecationWarning from httpx regarding per-request cookies:
- tests/test_auth_flow.py::test_refresh_rotation_revoked_old_token_and_session
- tests/test_session.py::test_refresh_token_replay_attack

Recommended follow-up: configure cookies on the AsyncClient instance.

================================================================================
EXECUTION COMMANDS
================================================================================
# Run all tests
uv run pytest

# Verbose output
uv run pytest -v

# Show skip reasons
uv run pytest -rs

================================================================================
END OF REPORT
================================================================================