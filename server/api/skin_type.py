from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db import SkinType
from db.session import session
from ..schemas.skin_type import SkinTypeCreate, SkinTypeUpdate, SkinTypeSchema

router = APIRouter(prefix="/skin-types", tags=["Skin Types"])


@router.get("/", response_model=List[SkinTypeSchema])
def get_all_skin_types():
    """Retrieve all skin types."""
    with session() as db:
        skin_types = db.query(SkinType).all()
        return skin_types


@router.get("/{skin_type_id}", response_model=SkinTypeSchema)
def get_skin_type(skin_type_id: int):
    """Retrieve a specific skin type by ID."""
    with session() as db:
        skin_type = db.query(SkinType).filter(SkinType.id == skin_type_id).first()
        if not skin_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skin type not found"
            )
        return skin_type


@router.post("/", response_model=SkinTypeSchema, status_code=status.HTTP_201_CREATED)
def create_skin_type(skin_type_data: SkinTypeCreate):
    """Create a new skin type."""
    with session() as db:
        try:
            new_skin_type = SkinType(name=skin_type_data.name)
            db.add(new_skin_type)
            db.flush()
            return new_skin_type
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skin type name already exists"
            )


@router.put("/{skin_type_id}", response_model=SkinTypeSchema)
def update_skin_type(skin_type_id: int, skin_type_data: SkinTypeUpdate):
    """Update an existing skin type."""
    with session() as db:
        skin_type = db.query(SkinType).filter(SkinType.id == skin_type_id).first()
        if not skin_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skin type not found"
            )
        
        try:
            skin_type.name = skin_type_data.name
            db.flush()
            return skin_type
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skin type name already exists"
            )


@router.delete("/{skin_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skin_type(skin_type_id: int):
    """Delete a skin type."""
    with session() as db:
        skin_type = db.query(SkinType).filter(SkinType.id == skin_type_id).first()
        if not skin_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skin type not found"
            )
        db.delete(skin_type)
