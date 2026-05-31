import json
import logging
from typing import Any

from db.config import config

from .redis_client import get_redis_client

logger = logging.getLogger(__name__)


def _product_card_key(product_id: int) -> str:
    return f"product:{product_id}:detail"


def get_product_card(product_id: int) -> dict[str, Any] | None:
    client = get_redis_client()
    if client is None:
        return None

    key = _product_card_key(product_id)
    try:
        cached = client.get(key)
    except Exception:
        logger.warning(
            "failed to read product card cache",
            extra={"product_id": product_id},
            exc_info=True,
        )
        return None

    if not cached:
        return None

    if isinstance(cached, bytes):
        cached = cached.decode("utf-8")

    try:
        payload = json.loads(cached)
    except json.JSONDecodeError:
        logger.warning(
            "invalid product card cache payload",
            extra={"product_id": product_id},
        )
        return None

    if not isinstance(payload, dict):
        logger.warning(
            "unexpected product card cache payload",
            extra={"product_id": product_id},
        )
        return None

    return payload


def set_product_card(product_id: int, payload: dict[str, Any]) -> None:
    client = get_redis_client()
    if client is None:
        return

    ttl_seconds = config.PRODUCT_CARD_CACHE_TTL_SECONDS
    if ttl_seconds <= 0:
        return

    key = _product_card_key(product_id)
    try:
        client.setex(key, ttl_seconds, json.dumps(payload, ensure_ascii=False))
    except Exception:
        logger.warning(
            "failed to write product card cache",
            extra={"product_id": product_id},
            exc_info=True,
        )


def invalidate_product_card(product_id: int) -> None:
    client = get_redis_client()
    if client is None:
        return

    key = _product_card_key(product_id)
    try:
        client.delete(key)
    except Exception:
        logger.warning(
            "failed to invalidate product card cache",
            extra={"product_id": product_id},
            exc_info=True,
        )
