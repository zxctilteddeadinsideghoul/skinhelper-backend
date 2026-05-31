import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("API_TOKEN", "test-token")

from server.image_cache_events import (
    build_product_image_cache_event,
    publish_product_image_cache_request,
)


class ImageCacheEventTests(unittest.TestCase):
    def test_build_event_returns_none_without_urls(self) -> None:
        product = SimpleNamespace(id=1, image_url=None, additional_image_urls=None)

        self.assertIsNone(build_product_image_cache_event(product))

    def test_build_event_includes_product_image_urls(self) -> None:
        product = SimpleNamespace(
            id=7,
            image_url="https://example.com/main.jpg",
            additional_image_urls=["https://example.com/extra.jpg"],
        )

        event = build_product_image_cache_event(product)

        self.assertIsNotNone(event)
        self.assertEqual(event["event_type"], "product.image_cache_requested")
        self.assertEqual(event["product_id"], 7)
        self.assertEqual(event["image_url"], "https://example.com/main.jpg")
        self.assertEqual(event["additional_image_urls"], ["https://example.com/extra.jpg"])
        self.assertIn("event_id", event)
        self.assertIn("occurred_at", event)

    def test_publish_failure_does_not_raise(self) -> None:
        product = SimpleNamespace(id=1, image_url="https://example.com/main.jpg", additional_image_urls=[])

        with patch("server.image_cache_events._get_producer", side_effect=RuntimeError("down")), patch(
            "server.image_cache_events.logger.exception"
        ):
            publish_product_image_cache_request(product)


if __name__ == "__main__":
    unittest.main()
