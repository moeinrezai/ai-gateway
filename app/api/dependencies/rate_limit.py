from fastapi import Depends, Request
from redis.asyncio import Redis
from app.core.exceptions.rate_limit import RateLimitExceededError
from app.core.rate_limit import check_rate_limit
from app.core.redis import get_redis


class IPRateLimiter:
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window

    async def __call__(
        self,
        request: Request,
        redis: Redis = Depends(get_redis),
    ) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rl:ip:{client_ip}"
        
        await check_rate_limit(redis, key, self.limit, self.window)


class AuthRateLimiter(IPRateLimiter):
    
    def __init__(self):
        from app.core.rate_limit import AUTH_IP_LIMIT, AUTH_IP_WINDOW
        super().__init__(limit=AUTH_IP_LIMIT, window=AUTH_IP_WINDOW)


class AIRateLimiter(IPRateLimiter):

    def __init__(self):
        from app.core.rate_limit import AI_IP_LIMIT, AI_IP_WINDOW
        super().__init__(limit=AI_IP_LIMIT, window=AI_IP_WINDOW)