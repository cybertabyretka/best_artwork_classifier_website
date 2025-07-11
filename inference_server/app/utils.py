import hashlib
from typing import Literal

import numpy as np
from redis import asyncio as aioredis
import redis


def softmax(x: np.ndarray) -> np.ndarray:
    """
    Compute the softmax of a vector or array of scores.

    The softmax function converts a vector of raw scores into
    probabilities that sum to 1. It is commonly used in
    classification tasks.
    :param x: (np.ndarray) Input array of scores.
    :return: np.ndarray Softmax probabilities with the same shape as the input.
    """
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


async def get_redis_aio(url) -> aioredis.Redis:
    return await aioredis.from_url(
        url=url,
        encoding="utf-8",
        decode_responses=True,
    )


def get_redis_sync(url: str = "redis://localhost:6379/0") -> redis.Redis:
    """
    Create a synchronous Redis client from URL.
    :param url: (str) Redis connection URL (e.g., "redis://user:pass@host:port/db").
                   Defaults to "redis://localhost:6379/0".
    :return: redis.Redis Synchronous Redis client instance.
    """
    return redis.from_url(url)


def make_cache_key(data_bytes: bytes) -> str:
    """Generate an SHA-256 based cache key for the input image bytes."""
    h = hashlib.sha256(data_bytes).hexdigest()
    return f"inference:{h}"


async def clear_redis_aio(
        redis_url: str,
        flush_mode: Literal["db", "all"] = "db"
) -> bool:
    """
    Clears a Redis database (either the current DB or all DBs) using aioredis.
    :param redis_url: (str) Redis connection URL (e.g., "redis://localhost:6379/0").
    :param flush_mode: (Literal["db", "all"])
    :return: bool True if the operation succeeded, False otherwise.
    """
    r = await get_redis_aio(redis_url)
    try:
        if flush_mode == "all":
            await r.flushall()
        else:
            await r.flushdb()
        return True
    except aioredis.RedisError as e:
        print(f"Error clearing Redis: {e}")
        return False
    finally:
        await r.close()


def clear_redis_sync(
        redis_url: str,
        flush_mode: Literal["db", "all"] = "db",
) -> bool:
    """
    Synchronously clears Redis database(s).
    :param redis_url: (str) Redis connection URL (e.g., "redis://localhost:6379/0").
    :param flush_mode: (Literal["db", "all"])
    :return: bool True if operation succeeded, False otherwise.
    """
    r = get_redis_sync(redis_url)
    try:
        if not r.ping():
            raise ConnectionError("Failed to connect to Redis")
        if flush_mode == "all":
            r.flushall()
        else:
            r.flushdb()
        return True
    except (redis.RedisError, ConnectionError) as e:
        print(f"Redis error: {e}")
        return False
    finally:
        if 'r' in locals():
            r.close()
