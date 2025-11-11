from .common import APIModel


class CategoryCreate(APIModel):
    name: str


class CategoryUpdate(APIModel):
    name: str


class CategorySchema(APIModel):
    id: int
    name: str