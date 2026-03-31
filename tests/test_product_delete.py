import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch

os.environ.setdefault("API_TOKEN", "test-token")

from fastapi import HTTPException
from fastapi.routing import APIRoute

from server.api.product import delete_product, router


class _FakeSession:
    def __init__(self, product):
        self.product = product
        self.deleted = None

    def get(self, model, product_id):
        return self.product

    def delete(self, product):
        self.deleted = product


class ProductDeleteTests(unittest.TestCase):
    def test_delete_route_is_configured_as_protected_204_delete(self) -> None:
        route = next(
            route
            for route in router.routes
            if isinstance(route, APIRoute) and route.path == "/products/{product_id}" and "DELETE" in route.methods
        )

        self.assertEqual(route.status_code, 204)

    def test_delete_product_deletes_existing_product(self) -> None:
        product = object()
        fake_session = _FakeSession(product)

        @contextmanager
        def fake_session_manager():
            yield fake_session

        with patch("server.api.product.session", fake_session_manager):
            result = delete_product(1)

        self.assertIsNone(result)
        self.assertIs(fake_session.deleted, product)

    def test_delete_product_raises_404_for_missing_product(self) -> None:
        fake_session = _FakeSession(None)

        @contextmanager
        def fake_session_manager():
            yield fake_session

        with patch("server.api.product.session", fake_session_manager):
            with self.assertRaises(HTTPException) as exc:
                delete_product(999)

        self.assertEqual(exc.exception.status_code, 404)
        self.assertEqual(exc.exception.detail, "Product not found")
        self.assertIsNone(fake_session.deleted)


if __name__ == "__main__":
    unittest.main()
