from typing import Optional
from .common import APIModel
from core.enums import SafetyLevel


class IngredientCreate(APIModel):
    name: str
    purpose: Optional[str] = None
    safety_level: SafetyLevel
    max_concentration: Optional[int] = None
    carcinogenicity: Optional[int] = None
    allergenicity: Optional[int] = None


class IngredientUpdate(APIModel):
    name: Optional[str] = None
    purpose: Optional[str] = None
    safety_level: SafetyLevel
    max_concentration: Optional[int] = None
    carcinogenicity: Optional[int] = None
    allergenicity: Optional[int] = None


class IngredientSchema(APIModel):
    id: int
    name: str
    purpose: Optional[str] = None
    safety_level: SafetyLevel
    max_concentration: Optional[int] = None
    carcinogenicity: Optional[int] = None
    allergenicity: Optional[int] = None