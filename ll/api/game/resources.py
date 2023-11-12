from enum import Enum
from typing import Callable, List

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
    size_multiplier_range: List[float]
    size_effect_multiplier: Callable


CONSUMABLES = [
    ConsumableDefinition(
        type=ConsumableType.APPLE,
        color=[0, 255, 0],
        size=10,
        spawn_ratio=0.7,
        player_size_diff=20,
        size_multiplier_range=[1.0, 4.0],
        # the effect applied is the inverse of the size (bigger fruit = smaller effect)
        size_effect_multiplier=lambda x: 1 / x,
    ),
    ConsumableDefinition(
        type=ConsumableType.POISON,
        color=[255, 0, 0],
        size=10,
        spawn_ratio=0.3,
        player_size_diff=-20,
        size_multiplier_range=[1, 3.0],
        # poison effect is constant regardless of size
        size_effect_multiplier=lambda x: x,
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
    effect_multiplier: float = 1.0


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
