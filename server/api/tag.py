from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from db import Tag
from db.session import session
from ..schemas.tag import TagCreate, TagUpdate, TagSchema

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/", response_model=List[TagSchema])
def get_all_tags():
    """Retrieve all tags."""
    with session() as db:
        tags = db.query(Tag).all()
        return tags


@router.get("/{tag_id}", response_model=TagSchema)
def get_tag(tag_id: int):
    """Retrieve a specific tag by ID."""
    with session() as db:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return tag


@router.post("/", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
def create_tag(tag_data: TagCreate):
    """Create a new tag."""
    with session() as db:
        try:
            new_tag = Tag(name=tag_data.name)
            db.add(new_tag)
            db.flush()
            return new_tag
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name already exists"
            )


@router.put("/{tag_id}", response_model=TagSchema)
def update_tag(tag_id: int, tag_data: TagUpdate):
    """Update an existing tag."""
    with session() as db:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        try:
            tag.name = tag_data.name
            db.flush()
            return tag
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name already exists"
            )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int):
    """Delete a tag."""
    with session() as db:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        db.delete(tag)
