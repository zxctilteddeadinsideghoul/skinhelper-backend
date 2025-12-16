import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List

from db import DeclBase
from core.enums import SafetyLevel


product_ingredients = sa.Table(
    "product_ingredients",
    DeclBase.metadata,
    sa.Column("product_id", sa.ForeignKey("products.id"), primary_key=True),
    sa.Column("ingredient_id", sa.ForeignKey("ingredients.id"), primary_key=True),
)

product_skin_types = sa.Table(
    "product_skin_types",
    DeclBase.metadata,
    sa.Column("product_id", sa.ForeignKey("products.id"), primary_key=True),
    sa.Column("skin_type_id", sa.ForeignKey("skin_types.id"), primary_key=True),
)

product_concerns = sa.Table(
    "product_concerns",
    DeclBase.metadata,
    sa.Column("product_id", sa.ForeignKey("products.id"), primary_key=True),
    sa.Column("concern_id", sa.ForeignKey("concerns.id"), primary_key=True),
)

product_tags = sa.Table(
    "product_tags",
    DeclBase.metadata,
    sa.Column("product_id", sa.ForeignKey("products.id"), primary_key=True),
    sa.Column("tag_id", sa.ForeignKey("tags.id"), primary_key=True),
)


class Brand(DeclBase):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="brand")


class Category(DeclBase):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")


class Ingredient(DeclBase):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
    purpose: Mapped[str] = mapped_column(sa.Text, nullable=True)

    safety_level: Mapped[SafetyLevel] = mapped_column(
        sa.Enum(
            SafetyLevel,
            name="safety_level_enum",
        ),
        nullable=False,
        server_default=SafetyLevel.safe.value,
    )

    max_concentration: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    carcinogenicity: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    allergenicity: Mapped[int] = mapped_column(sa.Integer, nullable=True)

    products: Mapped[List["Product"]] = relationship(
        secondary=product_ingredients,
        back_populates="ingredients",
    )


class SkinType(DeclBase):
    __tablename__ = "skin_types"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship(
        secondary=product_skin_types,
        back_populates="suitable_for_skin_types",
    )


class Concern(DeclBase):
    __tablename__ = "concerns"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship(
        secondary=product_concerns,
        back_populates="targets_concerns",
    )


class Tag(DeclBase):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)

    products: Mapped[List["Product"]] = relationship(
        secondary=product_tags,
        back_populates="tags",
    )


class Product(DeclBase):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    how_to_use: Mapped[str] = mapped_column(sa.Text, nullable=True)
    image_url: Mapped[str] = mapped_column(sa.String(300), nullable=True)
    volume_ml: Mapped[int] = mapped_column(sa.Integer, nullable=True)

    brand_id: Mapped[int] = mapped_column(sa.ForeignKey("brands.id"), nullable=True)
    category_id: Mapped[int] = mapped_column(sa.ForeignKey("categories.id"), nullable=True)

    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")

    ingredients: Mapped[List["Ingredient"]] = relationship(
        secondary=product_ingredients,
        back_populates="products",
    )

    suitable_for_skin_types: Mapped[List["SkinType"]] = relationship(
        secondary=product_skin_types,
        back_populates="products",
    )

    targets_concerns: Mapped[List["Concern"]] = relationship(
        secondary=product_concerns,
        back_populates="products",
    )

    tags: Mapped[List["Tag"]] = relationship(
        secondary=product_tags,
        back_populates="products",
    )
