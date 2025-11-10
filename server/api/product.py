from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from db import Product, Brand, Category, Ingredient, SkinType, Concern, Tag
from db.session import session
from ..schemas.product import ProductCreate, ProductUpdate, ProductShort

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductShort])
def get_all_products():
    with session() as s:
        products = s.query(Product).all()
        return products


@router.post("/", response_model=ProductShort, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate):
    with session() as s:
        # Проверка brand, если указан
        if product_in.brand_id is not None:
            brand = s.query(Brand).filter(Brand.id == product_in.brand_id).first()
            if not brand:
                raise HTTPException(status_code=400, detail="Brand not found")

        # Проверка category, если указана
        if product_in.category_id is not None:
            category = s.query(Category).filter(Category.id == product_in.category_id).first()
            if not category:
                raise HTTPException(status_code=400, detail="Category not found")

        # Создаём продукт
        product_data = product_in.model_dump(
            exclude={"ingredient_ids", "skin_type_ids", "concern_ids", "tag_ids"}
        )
        product = Product(**product_data)
        s.add(product)
        s.flush()

        # Загрузка и привязка связанных объектов (many-to-many)
        def set_relationship(attr_name: str, model_cls, id_list: Optional[List[int]]):
            if not id_list:
                return
            objs = s.query(model_cls).filter(model_cls.id.in_(id_list)).all()
            if len(objs) != len(id_list):
                raise HTTPException(status_code=400, detail=f"One or more {attr_name} not found")
            setattr(product, attr_name, objs)

        set_relationship("ingredients", Ingredient, product_in.ingredient_ids)
        set_relationship("suitable_for_skin_types", SkinType, product_in.skin_type_ids)
        set_relationship("targets_concerns", Concern, product_in.concern_ids)
        set_relationship("tags", Tag, product_in.tag_ids)

        s.commit()
        s.refresh(product)
        return product