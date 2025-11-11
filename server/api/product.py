from typing import Any, List, Optional, Type

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload, Session

from db import Product, Brand, Category, Ingredient, SkinType, Concern, Tag
from db.session import session
from ..schemas.product import ProductCreate, ProductUpdate, ProductShort

router = APIRouter(prefix="/products", tags=["Products"])


def _ensure_exists(db_session: Session, model: Type[Any], obj_id: int, name: str) -> Any:
    obj = db_session.get(model, obj_id)
    if not obj:
        raise HTTPException(status_code=400, detail=f"{name} not found")
    return obj


def _assign_m2m(
    db_session: Session,
    product_instance: Product,
    attr_name: str,
    model_cls: Type[Any],
    id_list: Optional[List[int]],
) -> None:
    if not id_list:
        return
    unique_ids = list(set(id_list))
    objs = db_session.query(model_cls).filter(model_cls.id.in_(unique_ids)).all()
    if len(objs) != len(unique_ids):
        missing = set(unique_ids) - {o.id for o in objs}
        raise HTTPException(
            status_code=400,
            detail=f"Some {attr_name} not found: {sorted(missing)}",
        )
    setattr(product_instance, attr_name, objs)


@router.get("/", response_model=List[ProductShort])
def get_all_products():
    with session() as s:
        products = (
            s.query(Product)
            .options(
                joinedload(Product.brand),
                joinedload(Product.category),
            )
            .all()
        )

        return products


@router.post("/", response_model=ProductShort, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate) -> ProductShort:
    with session() as s:
        # Validate foreign key references
        if product_in.brand_id:
            _ensure_exists(s, Brand, product_in.brand_id, "Brand")

        if product_in.category_id:
            _ensure_exists(s, Category, product_in.category_id, "Category")

        product_data = product_in.model_dump(
            exclude={"ingredient_ids", "skin_type_ids", "concern_ids", "tag_ids"}
        )
        product = Product(**product_data)
        s.add(product)
        s.flush()

        _assign_m2m(s, product, "ingredients", Ingredient, product_in.ingredient_ids)
        _assign_m2m(
            s, product, "suitable_for_skin_types", SkinType, product_in.skin_type_ids
        )
        _assign_m2m(s, product, "targets_concerns", Concern, product_in.concern_ids)
        _assign_m2m(s, product, "tags", Tag, product_in.tag_ids)

        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            raise HTTPException(
                status_code=400, detail="Product with this name already exists"
            )

        product = (
            s.query(Product)
            .options(
                selectinload(Product.brand),
                selectinload(Product.category),
            )
            .filter(Product.id == product.id)
            .one()
        )

        return product
