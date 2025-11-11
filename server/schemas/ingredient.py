from typing import Optional
from .common import APIModel


class IngredientCreate(APIModel):
    name: str
    purpose: Optional[str] = None


class IngredientUpdate(APIModel):
    name: Optional[str] = None
    purpose: Optional[str] = None


class IngredientSchema(APIModel):
    id: int
    name: str
    purpose: Optional[str] = None