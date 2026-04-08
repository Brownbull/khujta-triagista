"""Redis-backed rate limiting per reporter email.

Uses a sorted set per email with timestamps as scores for a sliding window.
Persists across container restarts via Redis.
Falls back to in-memory if Redis is unavailable (development/testing).
"""

import time
from collections import defaultdict
from dataclasses import dataclass

import redis

from app.config import settings

# Max incidents per reporter per window
MAX_INCIDENTS_PER_HOUR = 10
WINDOW_SECONDS = 3600
_KEY_PREFIX = "ratelimit:"


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    current_count: int
    limit: int
    retry_after_seconds: int | None


# Redis client (lazy init)
_redis: redis.Redis | None = None
# In-memory fallback for tests
_fallback: dict[str, list[float]] = defaultdict(list)
_use_fallback = False


def _get_redis() -> redis.Redis:
    """Get or create the Redis client."""
    global _redis, _use_fallback
    if _use_fallback:
        raise ConnectionError("Using fallback")
    if _redis is None:
        try:
            _redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            _redis.ping()
        except (redis.ConnectionError, redis.TimeoutError, OSError):
            _use_fallback = True
            raise ConnectionError("Redis unavailable, using fallback")
    return _redis


def check_rate_limit(reporter_email: str) -> RateLimitResult:
    """Check if a reporter has exceeded their rate limit."""
    now = time.time()
    window_start = now - WINDOW_SECONDS

    try:
        r = _get_redis()
        key = f"{_KEY_PREFIX}{reporter_email}"
        # Remove expired entries and count active ones in a pipeline
        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zrange(key, 0, 0, withscores=True)
        _, current, oldest_entries = pipe.execute()
    except (ConnectionError, redis.RedisError):
        return _check_rate_limit_fallback(reporter_email, now, window_start)

    if current >= MAX_INCIDENTS_PER_HOUR:
        oldest_ts = oldest_entries[0][1] if oldest_entries else now
        retry_after = int(oldest_ts + WINDOW_SECONDS - now) + 1
        return RateLimitResult(
            allowed=False,
            current_count=current,
            limit=MAX_INCIDENTS_PER_HOUR,
            retry_after_seconds=max(retry_after, 1),
        )

    return RateLimitResult(
        allowed=True,
        current_count=current,
        limit=MAX_INCIDENTS_PER_HOUR,
        retry_after_seconds=None,
    )


def record_submission(reporter_email: str) -> None:
    """Record a successful submission for rate limiting."""
    now = time.time()
    try:
        r = _get_redis()
        key = f"{_KEY_PREFIX}{reporter_email}"
        pipe = r.pipeline()
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, WINDOW_SECONDS)
        pipe.execute()
    except (ConnectionError, redis.RedisError):
        _fallback[reporter_email].append(now)


def reset_limits() -> None:
    """Reset all rate limits (for testing)."""
    global _redis, _use_fallback
    _fallback.clear()
    try:
        r = _get_redis()
        keys = r.keys(f"{_KEY_PREFIX}*")
        if keys:
            r.delete(*keys)
    except (ConnectionError, redis.RedisError):
        pass
    # Reset connection state so tests can switch modes
    _redis = None
    _use_fallback = False


def use_fallback_mode() -> None:
    """Force in-memory fallback (for testing without Redis)."""
    global _use_fallback
    _use_fallback = True


# --- In-memory fallback (mirrors old behavior) ---

def _check_rate_limit_fallback(
    reporter_email: str, now: float, window_start: float
) -> RateLimitResult:
    timestamps = _fallback[reporter_email]
    active = [t for t in timestamps if t > window_start]
    if active:
        _fallback[reporter_email] = active
    else:
        _fallback.pop(reporter_email, None)

    current = len(_fallback.get(reporter_email, []))

    if current >= MAX_INCIDENTS_PER_HOUR:
        oldest = min(_fallback[reporter_email])
        retry_after = int(oldest + WINDOW_SECONDS - now) + 1
        return RateLimitResult(
            allowed=False,
            current_count=current,
            limit=MAX_INCIDENTS_PER_HOUR,
            retry_after_seconds=max(retry_after, 1),
        )

    return RateLimitResult(
        allowed=True,
        current_count=current,
        limit=MAX_INCIDENTS_PER_HOUR,
        retry_after_seconds=None,
    )
