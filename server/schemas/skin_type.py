from .common import APIModel


class SkinTypeCreate(APIModel):
    name: str


class SkinTypeUpdate(APIModel):
    name: str


class SkinTypeSchema(APIModel):
    id: int
    name: str
