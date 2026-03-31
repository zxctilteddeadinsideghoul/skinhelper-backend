import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch

os.environ.setdefault("API_TOKEN", "test-token")

from sqlalchemy.dialects import postgresql

from server.api.product import (
    _apply_barcode_filter,
    _normalize_barcode,
    get_all_products,
)


def _call_get_all_products(**overrides):
    params = {
        "name": None,
        "brand": None,
        "search": None,
        "barcode": None,
        "category_id": None,
        "category": None,
        "skin_type_ids": None,
        "concern_ids": None,
        "tag_ids": None,
        "ingredient_ids": None,
        "skip": 0,
        "limit": None,
    }
    params.update(overrides)
    return get_all_products(**params)


class _FakeQuery:
    def __init__(self, results=None):
        self.results = [] if results is None else results
        self.filter_calls = []
        self.offset_value = None
        self.limit_value = None

    def options(self, *args, **kwargs):
        return self

    def outerjoin(self, *args, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        self.filter_calls.append((args, kwargs))
        return self

    def order_by(self, *args, **kwargs):
        return self

    def distinct(self, *args, **kwargs):
        return self

    def offset(self, value):
        self.offset_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def all(self):
        return self.results


class _FakeSession:
    def __init__(self, query):
        self._query = query

    def query(self, *args, **kwargs):
        return self._query


class ProductBarcodeSearchTests(unittest.TestCase):
    def test_normalize_barcode_removes_underscores(self) -> None:
        self.assertEqual(_normalize_barcode("ABC_12_3"), "ABC123")

    def test_exact_barcode_filter_uses_full_match(self) -> None:
        query = _FakeQuery()

        _apply_barcode_filter(query, "ABC_123", normalized=False)

        expression = query.filter_calls[0][0][0]
        sql = str(
            expression.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )
        self.assertIn("products.barcode = 'ABC_123'", sql)

    def test_normalized_barcode_filter_removes_underscores_in_sql(self) -> None:
        query = _FakeQuery()

        _apply_barcode_filter(query, "ABC_123", normalized=True)

        expression = query.filter_calls[0][0][0]
        sql = str(
            expression.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )
        self.assertIn("replace(coalesce(products.barcode, ''), '_', '') = 'ABC123'", sql)

    def test_get_all_products_prefers_exact_barcode_match(self) -> None:
        base_query = _FakeQuery()
        exact_query = _FakeQuery(results=["exact"])

        @contextmanager
        def fake_session_manager():
            yield _FakeSession(base_query)

        with patch("server.api.product.session", fake_session_manager), patch(
            "server.api.product._apply_barcode_filter",
            side_effect=[exact_query],
        ) as apply_barcode_filter, patch(
            "server.api.product._query_has_results",
            return_value=True,
        ) as query_has_results:
            result = _call_get_all_products(barcode="ABC_123")

        self.assertEqual(result, ["exact"])
        self.assertEqual(apply_barcode_filter.call_count, 1)
        self.assertEqual(apply_barcode_filter.call_args.kwargs["normalized"], False)
        query_has_results.assert_called_once_with(exact_query)

    def test_get_all_products_falls_back_to_normalized_barcode_match(self) -> None:
        base_query = _FakeQuery()
        exact_query = _FakeQuery()
        normalized_query = _FakeQuery(results=["normalized"])

        @contextmanager
        def fake_session_manager():
            yield _FakeSession(base_query)

        with patch("server.api.product.session", fake_session_manager), patch(
            "server.api.product._apply_barcode_filter",
            side_effect=[exact_query, normalized_query],
        ) as apply_barcode_filter, patch(
            "server.api.product._query_has_results",
            return_value=False,
        ) as query_has_results:
            result = _call_get_all_products(barcode="ABC_123")

        self.assertEqual(result, ["normalized"])
        self.assertEqual(apply_barcode_filter.call_count, 2)
        self.assertEqual(apply_barcode_filter.call_args_list[0].kwargs["normalized"], False)
        self.assertEqual(apply_barcode_filter.call_args_list[1].kwargs["normalized"], True)
        query_has_results.assert_called_once_with(exact_query)

    def test_barcode_filter_is_combined_with_other_filters(self) -> None:
        base_query = _FakeQuery()
        exact_query = _FakeQuery(results=["exact"])

        @contextmanager
        def fake_session_manager():
            yield _FakeSession(base_query)

        with patch("server.api.product.session", fake_session_manager), patch(
            "server.api.product._apply_barcode_filter",
            side_effect=[exact_query],
        ), patch(
            "server.api.product._query_has_results",
            return_value=True,
        ):
            _call_get_all_products(barcode="ABC_123", category_id=7)

        self.assertEqual(len(base_query.filter_calls), 1)


if __name__ == "__main__":
    unittest.main()
