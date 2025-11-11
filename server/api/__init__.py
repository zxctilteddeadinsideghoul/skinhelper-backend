from .product import router as product_router
from .brand import router as brand_router
from .category import router as category_router
from .ingredient import router as ingredient_router
from .skin_type import router as skin_type_router
from .concern import router as concern_router
from .tag import router as tag_router

__all__ = [
    "product_router",
    "brand_router",
    "category_router",
    "ingredient_router",
    "skin_type_router",
    "concern_router",
    "tag_router",
]
