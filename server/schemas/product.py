from typing import Optional, List
from .common import APIModel
from .ingredient import IngredientSchema
from .brand import BrandSchema
from .category import CategorySchema
from .skin_type import SkinTypeSchema
from .concern import ConcernSchema
from .tag import TagSchema


class ProductBase(APIModel):
    name: str
    description: Optional[str] = None
    how_to_use: Optional[str] = None
    image_url: Optional[str] = None
    volume_ml: Optional[int] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    """Используется при создании нового продукта."""
    ingredient_ids: Optional[List[int]] = None
    skin_type_ids: Optional[List[int]] = None
    concern_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class ProductUpdate(ProductBase):
    """Для PATCH/PUT операций."""
    ingredient_ids: Optional[List[int]] = None
    skin_type_ids: Optional[List[int]] = None
    concern_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class ProductShort(ProductBase):
    """Упрощённое представление продукта (например, для списка)."""
    id: int
    brand: Optional[BrandSchema] = None
    category: Optional[CategorySchema] = None


class ProductDetailed(ProductShort):
    """Детализированная схема продукта (как в твоём примере JSON)."""
    ingredients: List[IngredientSchema] = []
    suitable_for_skin_types: List[SkinTypeSchema] = []
    targets_concerns: List[ConcernSchema] = []
    tags: List[TagSchema] = []