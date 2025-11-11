from pydantic import ConfigDict
from pydantic.main import BaseModel


def to_pascal(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


class APIModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        populate_by_name=True,
        from_attributes=True,
    )