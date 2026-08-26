from fastapi import APIRouter

from app.api.v1.routers import auth, sessions, test, users

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(sessions.router)
router.include_router(users.router)
router.include_router(test.router)