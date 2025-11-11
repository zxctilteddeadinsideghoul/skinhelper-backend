from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db import Category
from db.session import session
from ..schemas.category import CategoryCreate, CategoryUpdate, CategorySchema

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategorySchema])
def get_all_categories():
    """Retrieve all categories."""
    with session() as db:
        categories = db.query(Category).all()
        return categories


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(category_id: int):
    """Retrieve a specific category by ID."""
    with session() as db:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate):
    """Create a new category."""
    with session() as db:
        try:
            new_category = Category(name=category_data.name)
            db.add(new_category)
            db.flush()
            return new_category
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(category_id: int, category_data: CategoryUpdate):
    """Update an existing category."""
    with session() as db:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        try:
            category.name = category_data.name
            db.flush()
            return category
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int):
    """Delete a category."""
    with session() as db:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        db.delete(category)
