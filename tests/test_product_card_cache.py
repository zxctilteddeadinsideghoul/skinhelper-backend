import json
import os
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("API_TOKEN", "test-token")

from fastapi import HTTPException

from server.api.product import get_product_detailed, update_product
from server.cache.product_cache import (
    get_product_card,
    invalidate_product_card,
    set_product_card,
)
from server.schemas.product import ProductUpdate


class _FakeQuery:
    def __init__(self, product=None):
        self.product = product

    def options(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.product

    def one(self):
        return self.product


class _FakeSession:
    def __init__(self, product=None):
        self.product = product

    def get(self, model, product_id):
        return self.product

    def query(self, *args, **kwargs):
        return _FakeQuery(self.product)


def _product(**overrides):
    data = {
        "id": 1,
        "name": "Serum",
        "barcode": None,
        "description": None,
        "how_to_use": None,
        "image_url": None,
        "additional_image_urls": None,
        "volume_ml": None,
        "brand_id": None,
        "category_id": None,
        "brand": None,
        "category": None,
        "ingredients": [],
        "suitable_for_skin_types": [],
        "targets_concerns": [],
        "tags": [],
    }
    data.update(overrides)
    return SimpleNamespace(**data)


class _FailingClient:
    def get(self, key):
        raise RuntimeError("redis down")

    def setex(self, key, ttl, value):
        raise RuntimeError("redis down")

    def delete(self, key):
        raise RuntimeError("redis down")


class ProductCacheModuleTests(unittest.TestCase):
    def test_get_product_card_returns_cached_payload(self) -> None:
        client = Mock()
        client.get.return_value = json.dumps({"id": 1, "name": "Serum"})

        with patch("server.cache.product_cache.get_redis_client", return_value=client):
            result = get_product_card(1)

        self.assertEqual(result, {"id": 1, "name": "Serum"})
        client.get.assert_called_once_with("product:1:detail")

    def test_get_product_card_returns_none_on_miss(self) -> None:
        client = Mock()
        client.get.return_value = None

        with patch("server.cache.product_cache.get_redis_client", return_value=client):
            result = get_product_card(1)

        self.assertIsNone(result)

    def test_product_cache_fails_open_when_redis_fails(self) -> None:
        with patch(
            "server.cache.product_cache.get_redis_client",
            return_value=_FailingClient(),
        ), patch("server.cache.product_cache.logger.warning"):
            self.assertIsNone(get_product_card(1))
            set_product_card(1, {"id": 1})
            invalidate_product_card(1)


class ProductDetailCacheTests(unittest.TestCase):
    def test_get_product_detailed_returns_cache_hit_without_db_query(self) -> None:
        cached = {
            "id": 1,
            "name": "Serum",
            "ingredients": [],
            "suitable_for_skin_types": [],
            "targets_concerns": [],
            "tags": [],
        }

        with patch("server.api.product.get_product_card", return_value=cached), patch(
            "server.api.product.session",
            side_effect=AssertionError("database should not be used"),
        ):
            result = get_product_detailed(1)

        self.assertEqual(result, cached)

    def test_get_product_detailed_caches_db_result_on_miss(self) -> None:
        product = _product()

        @contextmanager
        def fake_session_manager():
            yield _FakeSession(product)

        with patch("server.api.product.get_product_card", return_value=None), patch(
            "server.api.product.session",
            fake_session_manager,
        ), patch("server.api.product.set_product_card") as set_product_card_mock:
            result = get_product_detailed(1)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Serum")
        set_product_card_mock.assert_called_once_with(1, result)

    def test_get_product_detailed_does_not_cache_404(self) -> None:
        @contextmanager
        def fake_session_manager():
            yield _FakeSession(None)

        with patch("server.api.product.get_product_card", return_value=None), patch(
            "server.api.product.session",
            fake_session_manager,
        ), patch("server.api.product.set_product_card") as set_product_card_mock:
            with self.assertRaises(HTTPException) as exc:
                get_product_detailed(999)

        self.assertEqual(exc.exception.status_code, 404)
        set_product_card_mock.assert_not_called()

    def test_update_product_invalidates_card_cache(self) -> None:
        product = _product()

        @contextmanager
        def fake_session_manager():
            yield _FakeSession(product)

        with patch("server.api.product.session", fake_session_manager), patch(
            "server.api.product.invalidate_product_card"
        ) as invalidate_product_card_mock, patch(
            "server.api.product.publish_product_image_cache_request"
        ):
            update_product(1, ProductUpdate(name="Updated"))

        invalidate_product_card_mock.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
