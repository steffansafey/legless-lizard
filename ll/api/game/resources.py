from enum import Enum
from typing import List

from pydantic import dataclasses

TICK_PERIOD = 2
MINIMUM_STEP_LENGTH = 50
MIN_CONSUMABLE_COUNT = 50


class ConsumableType(Enum):
    APPLE = "apple"
    POISON = "poison"


@dataclasses.dataclass
class ConsumableDefinition:
    """A consumable definition."""

    type: ConsumableType
    color: List[int]
    size: int
    spawn_ratio: float


CONSUMABLES = [
    ConsumableDefinition(
        type=ConsumableType.APPLE,
        color=[0, 255, 0],
        size=10,
        spawn_ratio=0.9,
    ),
    ConsumableDefinition(
        type=ConsumableType.POISON,
        color=[255, 0, 0],
        size=10,
        spawn_ratio=0.1,
    ),
]


@dataclasses.dataclass
class PlayerStep:
    """A step a player took."""

    coordinates: List[float]


@dataclasses.dataclass
class GamePlayer:
    """A player in the game."""

    name: str
    id: str
    color: List[int]
    steps: List[PlayerStep]
    step_length: float
    spawned: bool
    angle: float = 0.0


@dataclasses.dataclass
class Consumable:
    """A consumable."""

    type: ConsumableType
    coordinates: List[float]
    size: int


@dataclasses.dataclass
class GameState:
    """The state of the game."""

    id: int
    tick: int
    tick_period: float
    server_timestamp: int
    server_next_tick_time: int
    players: List[GamePlayer]
    consumables: List[Consumable]
