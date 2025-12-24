from typing import Any, List, Optional, Type

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload, Session

from db import Product, Brand, Category, Ingredient, SkinType, Concern, Tag
from db.session import session
from ..schemas.product import ProductCreate, ProductUpdate, ProductShort, ProductDetailed

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


@router.get("/all", response_model=List[ProductShort])
def get_all_products(
    # Legacy parameters (maintained for backward compatibility)
    name: Optional[str] = Query(None, description="Search products by name (case-insensitive partial match) - deprecated, use 'search' instead"),
    brand: Optional[str] = Query(None, description="Search products by brand name (case-insensitive partial match) - deprecated, use 'search' instead"),

    # Unified search parameter
    search: Optional[str] = Query(None, description="Universal search across product name, brand name, category name, and ingredient names (case-insensitive partial match)"),

    # Category filters
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    category: Optional[str] = Query(None, description="Filter by category name (case-insensitive partial match)"),

    # Multi-select filters (many-to-many relationships)
    skin_type_ids: Optional[List[int]] = Query(None, description="Filter by suitable skin types (comma-separated IDs)"),
    concern_ids: Optional[List[int]] = Query(None, description="Filter by target concerns (comma-separated IDs)"),
    tag_ids: Optional[List[int]] = Query(None, description="Filter by product tags (comma-separated IDs)"),
    ingredient_ids: Optional[List[int]] = Query(None, description="Filter by ingredients (comma-separated IDs)"),

    # Pagination
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: Optional[int] = Query(None, description="Maximum number of records to return"),
):
    # Parameter validation
    if category_id and category:
        raise HTTPException(
            status_code=400,
            detail="Cannot specify both 'category_id' and 'category'. Use one or the other."
        )

    if name or brand:
        if search:
            raise HTTPException(
                status_code=400,
                detail="Cannot combine legacy 'name'/'brand' parameters with unified 'search' parameter. Use 'search' instead."
            )

    with session() as s:
        query = s.query(Product).options(
            selectinload(Product.brand),
            selectinload(Product.category),
        )

        if search:
            search_filter = (
                Product.name.ilike(f"%{search}%") |
                Brand.name.ilike(f"%{search}%") |
                Category.name.ilike(f"%{search}%") |
                Ingredient.name.ilike(f"%{search}%")
            )
            query = query.outerjoin(Product.brand).outerjoin(Product.category).outerjoin(Product.ingredients).filter(search_filter)

        elif name or brand:
            if name:
                query = query.filter(Product.name.ilike(f"%{name}%"))
            if brand:
                query = query.join(Product.brand).filter(Brand.name.ilike(f"%{brand}%"))

        if category_id:
            query = query.filter(Product.category_id == category_id)
        elif category:
            query = query.join(Product.category).filter(Category.name.ilike(f"%{category}%"))

        if skin_type_ids:
            query = query.join(Product.suitable_for_skin_types).filter(SkinType.id.in_(skin_type_ids))

        if concern_ids:
            query = query.join(Product.targets_concerns).filter(Concern.id.in_(concern_ids))

        if tag_ids:
            query = query.join(Product.tags).filter(Tag.id.in_(tag_ids))

        if ingredient_ids:
            query = query.join(Product.ingredients).filter(Ingredient.id.in_(ingredient_ids))

        # Добавляем сортировку по ID для корректной работы distinct и предсказуемого порядка
        query = query.order_by(Product.id)
        
        if any([skin_type_ids, concern_ids, tag_ids, ingredient_ids]):
            query = query.distinct(Product.id)
        
        if limit:
            query = query.offset(skip).limit(limit)
        else:
            query = query.offset(skip)

        products = query.all()
        return products

from fastapi import HTTPException
from sqlalchemy.orm import selectinload

@router.get("/{product_id}", response_model=ProductDetailed)
def get_product_detailed(product_id: int):
    with session() as s:
        product = (
            s.query(Product)
            .options(
                selectinload(Product.brand),
                selectinload(Product.category),
                selectinload(Product.ingredients),
                selectinload(Product.suitable_for_skin_types),
                selectinload(Product.targets_concerns),
                selectinload(Product.tags),
            )
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product


@router.post("/", response_model=ProductShort, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate) -> ProductShort:
    with session() as s:
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


@router.put("/{product_id}", response_model=ProductShort)
def update_product(product_id: int, product_in: ProductUpdate):
    with session() as s:
        product = s.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product_in.brand_id is not None:
            _ensure_exists(s, Brand, product_in.brand_id, "Brand")

        if product_in.category_id is not None:
            _ensure_exists(s, Category, product_in.category_id, "Category")

        update_data = product_in.model_dump(exclude_unset=True, exclude={"ingredient_ids", "skin_type_ids", "concern_ids", "tag_ids"})
        for field, value in update_data.items():
            setattr(product, field, value)

        if product_in.ingredient_ids is not None:
            _assign_m2m(s, product, "ingredients", Ingredient, product_in.ingredient_ids)
        if product_in.skin_type_ids is not None:
            _assign_m2m(s, product, "suitable_for_skin_types", SkinType, product_in.skin_type_ids)
        if product_in.concern_ids is not None:
            _assign_m2m(s, product, "targets_concerns", Concern, product_in.concern_ids)
        if product_in.tag_ids is not None:
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
            .filter(Product.id == product_id)
            .one()
        )

        return product