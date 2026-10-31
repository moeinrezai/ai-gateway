from fastapi import Depends, Request
from redis.asyncio import Redis

from app.core.rate_limit import check_rate_limit
from app.core.redis import get_redis


class IPRateLimiter:

    def __init__(self, limit: int, window: int, scope: str = "ip"):
        self.limit = limit
        self.window = window
        self.scope = scope

    async def __call__(
        self,
        request: Request,
        redis: Redis = Depends(get_redis),
    ) -> None:
        client_ip = getattr(request.state, "client_ip", None)
        if not client_ip and request.client:
            client_ip = request.client.host
        elif not client_ip:
            client_ip = "unknown"

        key = f"rl:{self.scope}:{client_ip}"

        await check_rate_limit(redis, key, self.limit, self.window)


class LoginRateLimiter(IPRateLimiter):

    def __init__(self):
        from app.core.rate_limit import AUTH_IP_WINDOW, LOGIN_IP_LIMIT

        super().__init__(limit=LOGIN_IP_LIMIT, window=AUTH_IP_WINDOW, scope="login")


class RegisterRateLimiter(IPRateLimiter):

    def __init__(self):
        from app.core.rate_limit import AUTH_IP_WINDOW, REGISTER_IP_LIMIT

        super().__init__(limit=REGISTER_IP_LIMIT, window=AUTH_IP_WINDOW, scope="register")


class AIRateLimiter(IPRateLimiter):

    def __init__(self):
        from app.core.rate_limit import AI_IP_LIMIT, AI_IP_WINDOW

        super().__init__(limit=AI_IP_LIMIT, window=AI_IP_WINDOW, scope="ai")
