from typing import List

from pydantic import dataclasses

from .buffs import Buff
from .consumables import Consumable

DEFAULT_TICK_PERIOD = 1.25
MINIMUM_STEP_LENGTH = 50
MAP_SIZE = 2000
CONSUMABLE_DENSITY = 0.00005
MIN_CONSUMABLE_COUNT = int((MAP_SIZE**2) * CONSUMABLE_DENSITY)


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
    buffs: List[Buff]
    spawned: bool
    step_fov: float
    is_bot: bool
    angle: float = 0.0


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
    global_buffs: List[Buff]
    map_bounds: List[List[float]]
