from .common import APIModel


class BrandCreate(APIModel):
    name: str


class BrandUpdate(APIModel):
    name: str


class BrandSchema(APIModel):
    id: int
    name: str