from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from ll.api.game.resources import GamePlayer

from .schema import BasePydanticSchema


class MessageType(Enum):
    """Enum for message types."""

    JOIN_REQUEST = "join_request"
    JOIN_RESPONSE = "join_response"
    STATE_UPDATE = "state_update"


class JoinRequest(BasePydanticSchema):
    """Join request."""

    name: str
    color: List[int]


class JoinResponse(BasePydanticSchema):
    """Join response."""

    player_id: Optional[str]
    ok: bool


class StateUpdate(BasePydanticSchema):
    """State update."""

    tick: int
    tick_period: float
    server_timestamp: datetime
    server_next_tick_time: datetime
    players: List[GamePlayer]


class MessageWrapper(BasePydanticSchema):
    """Wrapper for messages."""

    type: MessageType
    payload: Union[JoinRequest, JoinResponse, StateUpdate]
