from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db import Category
from db.session import session
from ..auth import require_api_token
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


@router.post(
    "/",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_token)],
)
def create_category(category_data: CategoryCreate):
    """Create a new category."""
    try:
        with session() as db:
            new_category = Category(name=category_data.name)
            db.add(new_category)
            db.flush()
            return new_category
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )


@router.put(
    "/{category_id}",
    response_model=CategorySchema,
    dependencies=[Depends(require_api_token)],
)
def update_category(category_id: int, category_data: CategoryUpdate):
    """Update an existing category."""
    try:
        with session() as db:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
            category.name = category_data.name
            db.flush()
            return category
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_token)],
)
def delete_category(category_id: int):
    """Delete a category."""
    try:
        with session() as db:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
            db.delete(category)
            db.flush()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category: it is still referenced by other records"
        )
