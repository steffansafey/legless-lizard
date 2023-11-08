from enum import Enum
from typing import List, Optional, Union

from .schema import BasePydanticSchema


class MessageType(Enum):
    """Enum for message types."""

    JOIN_REQUEST = "join_request"
    JOIN_RESPONSE = "join_response"


class JoinRequest(BasePydanticSchema):
    """Join request."""

    name: str
    color: List[int]


class JoinResponse(BasePydanticSchema):
    """Join response."""

    player_id: Optional[str]
    ok: bool


class MessageWrapper(BasePydanticSchema):
    """Wrapper for messages."""

    type: MessageType
    payload: Union[JoinRequest, JoinResponse]
