from typing import List

from pydantic import dataclasses


@dataclasses.dataclass
class PlayerStep:
    """A step a player took."""

    angle: float
    length: float


@dataclasses.dataclass
class GamePlayer:
    """A player in the game."""

    name: str
    id: str
    color: List[int]
    steps: List[PlayerStep]
    step_length: float


@dataclasses.dataclass
class GameState:
    """The state of the game."""

    id: int
    tick: int
    tick_period: float
    server_timestamp: int
    server_next_tick_time: int
    players: List[GamePlayer]