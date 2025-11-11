from .common import APIModel


class ConcernCreate(APIModel):
    name: str


class ConcernUpdate(APIModel):
    name: str


class ConcernSchema(APIModel):
    id: int
    name: str