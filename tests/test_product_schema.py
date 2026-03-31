import unittest

from server.schemas.product import ProductCreate, ProductShort


class ProductSchemaTests(unittest.TestCase):
    def test_product_create_accepts_barcode_with_underscore(self) -> None:
        product = ProductCreate(name="Serum", barcode="ABC_123")

        self.assertEqual(product.barcode, "ABC_123")
        self.assertEqual(product.model_dump()["barcode"], "ABC_123")

    def test_product_short_serializes_barcode_alias(self) -> None:
        product = ProductShort(id=1, name="Serum", barcode="SKU_42")

        self.assertEqual(product.model_dump(by_alias=True)["Barcode"], "SKU_42")

    def test_product_barcode_is_optional(self) -> None:
        product = ProductCreate(name="Serum")

        self.assertIsNone(product.barcode)


if __name__ == "__main__":
    unittest.main()
