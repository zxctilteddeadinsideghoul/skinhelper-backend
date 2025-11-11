from .common import APIModel


class TagCreate(APIModel):
    name: str


class TagUpdate(APIModel):
    name: str


class TagSchema(APIModel):
    id: int
    name: str