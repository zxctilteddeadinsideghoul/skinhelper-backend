from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db import Ingredient
from db.session import session
from ..schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientSchema

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get("/", response_model=List[IngredientSchema])
def get_all_ingredients():
    """Retrieve all ingredients."""
    with session() as db:
        ingredients = db.query(Ingredient).all()
        return ingredients


@router.get("/{ingredient_id}", response_model=IngredientSchema)
def get_ingredient(ingredient_id: int):
    """Retrieve a specific ingredient by ID."""
    with session() as db:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
        return ingredient


@router.post("/", response_model=IngredientSchema, status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient_data: IngredientCreate):
    """Create a new ingredient."""
    with session() as db:
        try:
            new_ingredient = Ingredient(
                name=ingredient_data.name,
                purpose=ingredient_data.purpose
            )
            db.add(new_ingredient)
            db.flush()
            return new_ingredient
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ingredient name already exists"
            )


@router.put("/{ingredient_id}", response_model=IngredientSchema)
def update_ingredient(ingredient_id: int, ingredient_data: IngredientUpdate):
    """Update an existing ingredient."""
    with session() as db:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
        
        try:
            if ingredient_data.name is not None:
                ingredient.name = ingredient_data.name
            if ingredient_data.purpose is not None:
                ingredient.purpose = ingredient_data.purpose
            db.flush()
            return ingredient
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ingredient name already exists"
            )


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int):
    """Delete an ingredient."""
    with session() as db:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
        db.delete(ingredient)
