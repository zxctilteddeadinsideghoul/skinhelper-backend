import os
import unittest

os.environ.setdefault("API_TOKEN", "test-token")

from fastapi import HTTPException
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials

from server.auth import require_api_token
from server.api import (
    brand_router,
    category_router,
    concern_router,
    ingredient_router,
    product_router,
    skin_type_router,
    tag_router,
)


class ApiAuthTests(unittest.TestCase):
    def test_write_without_token_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as exc:
            require_api_token(None)

        self.assertEqual(exc.exception.status_code, 401)
        self.assertEqual(exc.exception.detail, "Missing API token")

    def test_write_with_invalid_token_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as exc:
            require_api_token(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="wrong-token",
                )
            )

        self.assertEqual(exc.exception.status_code, 401)
        self.assertEqual(exc.exception.detail, "Invalid API token")

    def test_write_with_valid_token_is_allowed(self) -> None:
        result = require_api_token(
            HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="test-token",
            )
        )

        self.assertIsNone(result)

    def test_only_write_routes_require_token(self) -> None:
        routers = [
            brand_router,
            category_router,
            concern_router,
            ingredient_router,
            product_router,
            skin_type_router,
            tag_router,
        ]

        for router in routers:
            for route in router.routes:
                if not isinstance(route, APIRoute):
                    continue

                has_auth_dependency = any(
                    dependency.call is require_api_token
                    for dependency in route.dependant.dependencies
                )

                if "GET" in route.methods:
                    self.assertFalse(
                        has_auth_dependency,
                        f"GET route {route.path} should stay public",
                    )
                else:
                    self.assertTrue(
                        has_auth_dependency,
                        f"Write route {route.path} should require API token",
                    )


if __name__ == "__main__":
    unittest.main()
