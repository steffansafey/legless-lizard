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
    player_size_diff: int


CONSUMABLES = [
    ConsumableDefinition(
        type=ConsumableType.APPLE,
        color=[0, 255, 0],
        size=10,
        spawn_ratio=0.9,
        player_size_diff=20,
    ),
    ConsumableDefinition(
        type=ConsumableType.POISON,
        color=[255, 0, 0],
        size=10,
        spawn_ratio=0.1,
        player_size_diff=-20,
    ),
]


def get_consumable_definition(consumable_type: ConsumableType):
    """Get a consumable definition by type."""
    return next((d for d in CONSUMABLES if d.type == consumable_type))


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
