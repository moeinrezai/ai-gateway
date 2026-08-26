from fastapi import APIRouter, Depends

from app.api.dependencies.rate_limit import IPRateLimiter

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/rate-limit")
async def test_rate_limit(_: None = Depends(IPRateLimiter(limit=5, window=60))):
    return {"message": "You are within the rate limit."}
