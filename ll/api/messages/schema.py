from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


def _camel_alias_generator(string) -> str:
    """Convert a snake_case string to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class BasePydanticSchema(BaseModel):
    """Base class for all pydantic schemas."""

    class Config:
        json_encoders = {
            # Convert datetimes to timestamps in milliseconds.
            datetime: lambda v: int(v.timestamp() * 1000),
            # Convert decimals to 2dp string
            Decimal: lambda v: round(float(Decimal(v)), 2),
            Enum: lambda v: v.name.lower(),
        }

        arbitrary_types_allowed = False

        # input & output is in camelCase
        alias_generator = _camel_alias_generator

        # allows us to use snake_case in the code (PEP8)
        populate_by_name = True

    def json(self, *args, **kwargs):
        return super().json(*args, **kwargs, by_alias=True)
