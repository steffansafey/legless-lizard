import dataclasses
from enum import Enum
from typing import Callable, List
from uuid import uuid4

from .buffs import BUFF_DEFINITIONS, Buff, BuffType


class ConsumableType(Enum):
    APPLE = "apple"
    POISON = "poison"
    PINEAPPLE = "pineapple"
    GRAPE = "grape"
    STONE = "stone"


CONSUMABLE_TO_BUFF_MAP = {
    ConsumableType.PINEAPPLE: BUFF_DEFINITIONS[BuffType.APPLE_MAGNET],
    ConsumableType.POISON: BUFF_DEFINITIONS[BuffType.APPLE_REPEL],
    ConsumableType.GRAPE: BUFF_DEFINITIONS[BuffType.TICK_PERIOD_BOOST],
    ConsumableType.STONE: BUFF_DEFINITIONS[BuffType.GHOST],
}


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


CONSUMABLE_DEFINITIONS = [
    ConsumableDefinition(
        type=ConsumableType.APPLE,
        color=[0, 129, 72],
        size=10,
        spawn_ratio=0.8,
        player_size_diff=20,
        size_multiplier_range=[1.0, 2.0],
        # the effect applied is the inverse of the size (bigger fruit = smaller effect)
        size_effect_multiplier=lambda x: 1 / x,
    ),
    ConsumableDefinition(
        type=ConsumableType.POISON,
        color=[245, 65, 0],
        size=10,
        spawn_ratio=0.3,
        player_size_diff=-20,
        size_multiplier_range=[1, 3.0],
        # poison effect is constant regardless of size
        size_effect_multiplier=lambda x: x,
    ),
    ConsumableDefinition(
        type=ConsumableType.PINEAPPLE,
        color=[247, 203, 21],
        size=10,
        spawn_ratio=0.1,
        player_size_diff=0,
        size_multiplier_range=[1, 1],
        size_effect_multiplier=lambda x: x,
    ),
    ConsumableDefinition(
        type=ConsumableType.GRAPE,
        color=[181, 129, 197],
        size=10,
        spawn_ratio=0.2,
        player_size_diff=0,
        size_multiplier_range=[1, 1],
        size_effect_multiplier=lambda x: x,
    ),
    ConsumableDefinition(
        type=ConsumableType.STONE,
        color=[143, 143, 143],
        size=10,
        spawn_ratio=0.3,
        player_size_diff=0,
        size_multiplier_range=[1, 1.3],
        size_effect_multiplier=lambda x: x,
    ),
]


@dataclasses.dataclass
class Consumable:
    """A consumable."""

    type: ConsumableType
    coordinates: List[float]
    size: int
    color: List[int]
    effect_multiplier: float = 1.0
    uid: str = dataclasses.field(default_factory=lambda: str(uuid4()))

    @property
    def definition(self):
        """Get the consumable definition."""
        return next((d for d in CONSUMABLE_DEFINITIONS if d.type == self.type), None)

    @property
    def buff(self):
        """Get the buff that this consumable applies."""
        buff_definition = CONSUMABLE_TO_BUFF_MAP.get(self.type, None)

        if not buff_definition:
            return None

        return Buff(
            type=buff_definition.type,
            friendly_name=buff_definition.friendly_name,
            is_debuff=buff_definition.is_debuff,
            duration_remaining=buff_definition.default_duration,
            duration=buff_definition.default_duration,
            is_applied=False,
        )
