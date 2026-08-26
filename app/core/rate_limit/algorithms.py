import time

import redis.asyncio as aioredis

from app.core.exceptions.rate_limit import RateLimitExceededError

# Lua script for atomic sliding window rate limiting
# Uses Sorted Set where score is timestamp and member is unique request ID
SLIDING_WINDOW_LUA_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local window_start = now - window

-- Remove entries outside the current window
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

-- Count current entries in the window
local count = redis.call('ZCARD', key)

if count >= limit then
    -- Get the oldest entry to calculate retry_after
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry_after = 0
    if #oldest > 0 then
        retry_after = math.ceil(tonumber(oldest[2]) + window - now)
    end
    return {0, retry_after}
end

-- Add new entry with unique member (timestamp + random)
local member = now .. '-' .. math.random(1000000)
redis.call('ZADD', key, now, member)

-- Set expiry to auto-cleanup old keys
redis.call('EXPIRE', key, window + 1)

return {1, 0}
"""


async def check_rate_limit(
    redis: aioredis.Redis,
    key: str,
    limit: int,
    window: int,
) -> None:
    """
    Checks if the request is within the rate limit.
    Raises RateLimitExceededError if limit is exceeded.
    
    Args:
        redis: Redis client instance
        key: Unique identifier for the rate limit bucket (e.g., "rl:ip:192.168.1.1")
        limit: Maximum number of requests allowed in the window
        window: Time window in seconds
    """
    now = time.time()
    
    result = await redis.eval(
        SLIDING_WINDOW_LUA_SCRIPT,
        1,  # number of keys
        key,
        limit,
        window,
        now,
    )
    
    allowed, retry_after = result[0], result[1]
    
    if not allowed:
        raise RateLimitExceededError(
            message=f"Rate limit exceeded. Try again in {int(retry_after)} seconds.",
            retry_after=int(retry_after),
        )