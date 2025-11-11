from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db import Concern
from db.session import session
from ..schemas.concern import ConcernCreate, ConcernUpdate, ConcernSchema

router = APIRouter(prefix="/concerns", tags=["Concerns"])


@router.get("/", response_model=List[ConcernSchema])
def get_all_concerns():
    """Retrieve all concerns."""
    with session() as db:
        concerns = db.query(Concern).all()
        return concerns


@router.get("/{concern_id}", response_model=ConcernSchema)
def get_concern(concern_id: int):
    """Retrieve a specific concern by ID."""
    with session() as db:
        concern = db.query(Concern).filter(Concern.id == concern_id).first()
        if not concern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concern not found"
            )
        return concern


@router.post("/", response_model=ConcernSchema, status_code=status.HTTP_201_CREATED)
def create_concern(concern_data: ConcernCreate):
    """Create a new concern."""
    with session() as db:
        try:
            new_concern = Concern(name=concern_data.name)
            db.add(new_concern)
            db.flush()
            return new_concern
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Concern name already exists"
            )


@router.put("/{concern_id}", response_model=ConcernSchema)
def update_concern(concern_id: int, concern_data: ConcernUpdate):
    """Update an existing concern."""
    with session() as db:
        concern = db.query(Concern).filter(Concern.id == concern_id).first()
        if not concern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concern not found"
            )
        
        try:
            concern.name = concern_data.name
            db.flush()
            return concern
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Concern name already exists"
            )


@router.delete("/{concern_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concern(concern_id: int):
    """Delete a concern."""
    with session() as db:
        concern = db.query(Concern).filter(Concern.id == concern_id).first()
        if not concern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Concern not found"
            )
        db.delete(concern)
