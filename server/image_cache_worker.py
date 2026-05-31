import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from kafka import KafkaConsumer

from db import Product
from db.config import config
from db.connection import start_db_connections, stop_db_connections
from db.session import session

logger = logging.getLogger(__name__)


def _bootstrap_servers() -> list[str]:
    return [
        server.strip()
        for server in config.KAFKA_BOOTSTRAP_SERVERS.split(",")
        if server.strip()
    ]


def _is_cached_url(url: str) -> bool:
    public_base = config.IMAGES_PUBLIC_URL.rstrip("/")
    internal_base = config.IMAGESERVICE_INTERNAL_URL.rstrip("/")
    return url.startswith(public_base + "/") or url.startswith(internal_base + "/")


def _cache_image_url(url: str) -> str:
    cleaned = url.strip()
    if not cleaned or _is_cached_url(cleaned):
        return cleaned

    body = json.dumps({"url": cleaned}).encode("utf-8")
    request = Request(
        f"{config.IMAGESERVICE_INTERNAL_URL.rstrip('/')}/images",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=config.IMAGE_CACHE_REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["url"]
    except HTTPError as exc:
        if 400 <= exc.code < 500:
            logger.warning(
                "image cache request rejected",
                extra={"url": cleaned, "status": exc.code},
            )
            return cleaned
        raise
    except (URLError, TimeoutError):
        raise


def process_image_cache_event(event: dict) -> None:
    product_id = event.get("product_id")
    if not product_id:
        logger.warning("image cache event missing product_id", extra={"event": event})
        return

    image_url = event.get("image_url")
    additional_urls = event.get("additional_image_urls") or []

    with session() as db_session:
        product = db_session.get(Product, product_id)
        if product is None:
            logger.info(
                "product no longer exists, skipping image cache event",
                extra={"product_id": product_id},
            )
            return

        if image_url:
            product.image_url = _cache_image_url(image_url)

        if additional_urls:
            product.additional_image_urls = [
                _cache_image_url(url)
                for url in additional_urls
                if url
            ]


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    start_db_connections()
    consumer = KafkaConsumer(
        config.KAFKA_IMAGE_CACHE_TOPIC,
        bootstrap_servers=_bootstrap_servers(),
        group_id=config.KAFKA_IMAGE_CACHE_GROUP,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    logger.info(
        "image cache worker started",
        extra={"topic": config.KAFKA_IMAGE_CACHE_TOPIC},
    )
    try:
        for message in consumer:
            try:
                process_image_cache_event(message.value)
            except Exception:
                logger.exception("failed to process image cache event")
                continue

            consumer.commit()
    finally:
        consumer.close()
        stop_db_connections()


if __name__ == "__main__":
    run()
