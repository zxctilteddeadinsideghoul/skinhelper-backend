import json
import os
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("API_TOKEN", "test-token")

from server.image_cache_worker import _cache_image_url, process_image_cache_event


class _FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps({"url": "http://localhost/cached.jpg"}).encode("utf-8")


class _FakeSession:
    def __init__(self, product):
        self.product = product

    def get(self, model, product_id):
        return self.product


class ImageCacheWorkerTests(unittest.TestCase):
    def test_cache_image_url_skips_already_cached_public_url(self) -> None:
        with patch("server.image_cache_worker.urlopen") as urlopen_mock:
            result = _cache_image_url("http://localhost/p/main.jpg")

        self.assertEqual(result, "http://localhost/p/main.jpg")
        urlopen_mock.assert_not_called()

    def test_cache_image_url_posts_to_imageservice(self) -> None:
        with patch("server.image_cache_worker.urlopen", return_value=_FakeResponse()):
            result = _cache_image_url("https://example.com/main.jpg")

        self.assertEqual(result, "http://localhost/cached.jpg")

    def test_process_image_cache_event_updates_product_urls(self) -> None:
        product = SimpleNamespace(image_url=None, additional_image_urls=None)

        @contextmanager
        def fake_session_manager():
            yield _FakeSession(product)

        with patch("server.image_cache_worker.session", fake_session_manager), patch(
            "server.image_cache_worker._cache_image_url",
            side_effect=lambda url: f"cached:{url}",
        ), patch("server.image_cache_worker.invalidate_product_card") as invalidate_product_card_mock:
            process_image_cache_event(
                {
                    "product_id": 1,
                    "image_url": "https://example.com/main.jpg",
                    "additional_image_urls": ["https://example.com/extra.jpg"],
                }
            )

        self.assertEqual(product.image_url, "cached:https://example.com/main.jpg")
        self.assertEqual(product.additional_image_urls, ["cached:https://example.com/extra.jpg"])
        invalidate_product_card_mock.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
