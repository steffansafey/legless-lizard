from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from ...game.resources.buffs import Buff
from ...game.resources.game import Consumable, GamePlayer
from .schema import BasePydanticSchema


class MessageType(Enum):
    """Enum for message types."""

    JOIN_REQUEST = "join_request"
    JOIN_RESPONSE = "join_response"
    STATE_UPDATE = "state_update"
    CLIENT_UPDATE = "client_update"


class JoinRequest(BasePydanticSchema):
    """Join request."""

    name: str
    color: List[int]


class JoinResponse(BasePydanticSchema):
    """Join response."""

    player_id: Optional[str]
    ok: bool
    reason: Optional[str]


class StateUpdate(BasePydanticSchema):
    """State update."""

    tick: int
    tick_period: float
    server_timestamp: datetime
    server_next_tick_time: datetime
    players: List[GamePlayer]
    consumables: List[Consumable]
    global_buffs: List[Buff]
    map_bounds: List[List[float]]


class ClientUpdate(BasePydanticSchema):
    """State update."""

    tick: int
    player_id: str
    angle: float


class MessageWrapper(BasePydanticSchema):
    """Wrapper for messages."""

    type: MessageType
    payload: Union[JoinRequest, JoinResponse, StateUpdate, ClientUpdate]
