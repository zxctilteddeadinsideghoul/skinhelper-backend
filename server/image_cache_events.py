import json
import logging
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

from kafka import KafkaProducer

from db.config import config

logger = logging.getLogger(__name__)

_producer: KafkaProducer | None = None


def _bootstrap_servers() -> list[str]:
    return [
        server.strip()
        for server in config.KAFKA_BOOTSTRAP_SERVERS.split(",")
        if server.strip()
    ]


def _get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=_bootstrap_servers(),
            key_serializer=lambda value: value.encode("utf-8"),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            max_block_ms=config.KAFKA_PRODUCER_MAX_BLOCK_MS,
            retries=0,
        )
    return _producer


def _compact_urls(urls: Iterable[str | None]) -> list[str]:
    result = []
    seen = set()
    for url in urls:
        if not url:
            continue
        cleaned = url.strip()
        if cleaned and cleaned not in seen:
            result.append(cleaned)
            seen.add(cleaned)
    return result


def build_product_image_cache_event(product: Any) -> dict[str, Any] | None:
    image_url = getattr(product, "image_url", None)
    additional_urls = getattr(product, "additional_image_urls", None) or []
    urls = _compact_urls([image_url, *additional_urls])
    if not urls:
        return None

    return {
        "event_id": str(uuid4()),
        "event_type": "product.image_cache_requested",
        "product_id": getattr(product, "id"),
        "image_url": image_url,
        "additional_image_urls": additional_urls,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }


def publish_product_image_cache_request(product: Any) -> None:
    event = build_product_image_cache_event(product)
    if event is None:
        return

    try:
        producer = _get_producer()
        producer.send(
            config.KAFKA_IMAGE_CACHE_TOPIC,
            key=str(event["product_id"]),
            value=event,
        )
        producer.flush(timeout=config.KAFKA_PRODUCER_FLUSH_TIMEOUT)
    except Exception:
        logger.exception(
            "failed to publish product image cache event",
            extra={"product_id": event.get("product_id")},
        )
