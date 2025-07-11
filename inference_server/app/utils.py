import hashlib
from typing import Literal, Dict, Any, Union

import numpy as np
import redis
from redis import asyncio as aioredis


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


def get_redis_aio(
    redis_url: str,
    decode_responses: bool = True,
    encoding: str = "utf-8",
    **kwargs
) -> aioredis.Redis:
    """
    Makes an asinc connection to Redis.
    :param redis_url: Redis URL.
    :param decode_responses: Decode bytes to strings (Yes/No)
    :param encoding: Coding
    :param kwargs: Extra parameters to aioredis.from_url function
    :return: Redis asinc client
    """
    return aioredis.from_url(
        url=redis_url,
        decode_responses=decode_responses,
        encoding=encoding,
        **kwargs
    )


def get_redis_sync(redis_url: str, **kwargs) -> redis.Redis:
    """
    Create a synchronous Redis client connection.
    :param redis_url: Redis connection URL (e.g. "redis://localhost:6379/0").
    :param kwargs: Additional arguments passed to redis.from_url.
    :return: A redis.Redis client instance.
    """
    return redis.from_url(redis_url, **kwargs)


def make_cache_key(data_bytes: bytes) -> str:
    """
    Generate a deterministic cache key for given bytes using SHA-256.
    :param data_bytes: The data in bytes for which to generate the key.
    :return: A string in the format "inference:<sha256_hash>".
    """
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


def scan_all_redis_data(
        redis_url: str = "redis://localhost:6379/0",
        pattern: str = "*",
        count: int = 1000,
        decode_responses: bool = True,
        encoding: str = "utf-8",
        cast_numbers: bool = False,
        **kwargs
) -> Dict[str, Any]:
    """
    Scan all keys in a Redis database and retrieve their values.

    Supports fetching all types of Redis data (strings, hashes,
    lists, sets, sorted sets). Optionally casts values to numbers
    if possible.
    :param redis_url: Redis connection URL (e.g. "redis://localhost:6379/0").
    :param pattern: SCAN pattern to match keys.
    :param count: Number of keys to scan per iteration.
    :param decode_responses: Whether to decode bytes to strings.
    :param encoding: Encoding for decoded responses.
    :param cast_numbers: Whether to cast string values to int/float when possible.
    :param kwargs: Additional parameters for redis.from_url().
    :return: A dictionary of keys and their corresponding values.
    """
    result = {}
    r = get_redis_sync(
        redis_url,
        decode_responses=decode_responses,
        encoding=encoding,
        **kwargs
    )

    try:
        cursor = 0
        while True:
            cursor, keys = r.scan(
                cursor=cursor,
                match=pattern,
                count=count
            )

            for key in keys:
                key_type = r.type(key)
                if key_type == 'string':
                    value = r.get(key)
                    if cast_numbers:
                        value = try_cast_number(value)
                elif key_type == 'hash':
                    value = r.hgetall(key)
                    if cast_numbers:
                        value = {k: try_cast_number(v) for k, v in value.items()}
                elif key_type == 'list':
                    value = r.lrange(key, 0, -1)
                    if cast_numbers:
                        value = [try_cast_number(v) for v in value]
                elif key_type == 'set':
                    value = r.smembers(key)
                    if cast_numbers:
                        value = {try_cast_number(v) for v in value}
                elif key_type == 'zset':
                    value = r.zrange(key, 0, -1, withscores=True)
                    if cast_numbers:
                        value = [(try_cast_number(member), score) for member, score in value]
                else:
                    value = None

                result[key] = value

            if cursor == 0:
                break

        return result

    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return {}
    finally:
        if hasattr(r, "connection_pool"):
            r.connection_pool.disconnect()


def try_cast_number(value: Union[str, bytes]) -> Union[int, float, str, bytes]:
    """
    Attempt to cast a string or bytes to int or float.

    If the value represents a numeric string, returns
    the corresponding number. Otherwise, returns the
    original value as a string.
    :param value: String or bytes value.
    :return: int, float, or original string.
    """
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")

    if isinstance(value, str):
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
    return value
