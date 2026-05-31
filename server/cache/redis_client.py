import logging
from typing import Any

from db.config import config

logger = logging.getLogger(__name__)

_client: Any | None = None
_import_failed = False


def get_redis_client() -> Any | None:
    global _client, _import_failed

    if _client is not None:
        return _client
    if _import_failed:
        return None

    try:
        import redis
    except ImportError:
        _import_failed = True
        logger.warning("redis package is not installed; product cache is disabled")
        return None

    _client = redis.Redis.from_url(
        config.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )
    return _client


def close_redis_connection() -> None:
    global _client

    if _client is None:
        return

    try:
        _client.close()
    except Exception:
        logger.warning("failed to close redis connection", exc_info=True)
    finally:
        _client = None
