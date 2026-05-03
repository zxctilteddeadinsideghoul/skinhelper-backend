from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db import Brand
from db.session import session
from ..auth import require_api_token
from ..schemas.brand import BrandCreate, BrandUpdate, BrandSchema

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.get("/", response_model=List[BrandSchema])
def get_all_brands():
    """Retrieve all brands."""
    with session() as db:
        brands = db.query(Brand).all()
        return brands


@router.get("/{brand_id}", response_model=BrandSchema)
def get_brand(brand_id: int):
    """Retrieve a specific brand by ID."""
    with session() as db:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        return brand


@router.post(
    "/",
    response_model=BrandSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_token)],
)
def create_brand(brand_data: BrandCreate):
    """Create a new brand."""
    with session() as db:
        try:
            new_brand = Brand(name=brand_data.name)
            db.add(new_brand)
            db.flush()
            return new_brand
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand name already exists"
            )


@router.put(
    "/{brand_id}",
    response_model=BrandSchema,
    dependencies=[Depends(require_api_token)],
)
def update_brand(brand_id: int, brand_data: BrandUpdate):
    """Update an existing brand."""
    with session() as db:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        
        try:
            brand.name = brand_data.name
            db.flush()
            return brand
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand name already exists"
            )


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_token)],
)
def delete_brand(brand_id: int):
    """Delete a brand."""
    with session() as db:
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        try:
            db.delete(brand)
            db.flush()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete brand: it is still referenced by other records"
            )
