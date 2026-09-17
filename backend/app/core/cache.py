"""Small JSON cache. Uses Redis when reachable and falls back to an in-process dict."""

import json
import logging
import time
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

log = logging.getLogger(__name__)


class Cache:
    def __init__(self, url: str) -> None:
        self._redis: redis.Redis = redis.from_url(url, decode_responses=True)
        self._memory: dict[str, tuple[float, Any]] = {}
        self._redis_ok = True

    async def get(self, key: str) -> Any | None:
        if self._redis_ok:
            try:
                raw = await self._redis.get(key)
                return json.loads(raw) if raw is not None else None
            except (redis.RedisError, OSError) as exc:
                self._degrade(exc)
        entry = self._memory.get(key)
        if entry is not None and entry[0] > time.monotonic():
            return entry[1]
        self._memory.pop(key, None)
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if self._redis_ok:
            try:
                await self._redis.set(key, json.dumps(value), ex=ttl_seconds)
                return
            except (redis.RedisError, OSError) as exc:
                self._degrade(exc)
        self._memory[key] = (time.monotonic() + ttl_seconds, value)

    def _degrade(self, exc: Exception) -> None:
        self._redis_ok = False
        log.warning("Redis unavailable (%s); using in-memory cache for this process", exc)

    async def close(self) -> None:
        await self._redis.aclose()


cache = Cache(settings.redis_url)
