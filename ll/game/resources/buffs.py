from enum import Enum
from typing import Optional

from pydantic import dataclasses


class BuffType(Enum):
    APPLE_MAGNET = "apple_magnet"
    APPLE_REPEL = "apple_repel"
    TICK_PERIOD_BOOST = "tick_period_boost"
    GHOST = "ghost"


class BuffApplicationTime(Enum):
    PRE_STEP = "pre_step"
    POST_STEP = "post_step"


class BuffApplicationFrequency(Enum):
    # applied once when the buff is first applied
    ONCE = "once"
    # each tick the buff is applied
    REPEATING = "repeating"


@dataclasses.dataclass
class BuffDefinition:
    type: BuffType
    friendly_name: str
    default_duration: int
    is_debuff: bool
    application_frequency: BuffApplicationFrequency
    application_time: BuffApplicationTime
    applies_globally: bool


@dataclasses.dataclass
class Buff:
    type: BuffType
    friendly_name: str
    is_debuff: bool
    is_applied: bool
    duration: Optional[int]
    duration_remaining: Optional[int]

    @property
    def definition(self) -> BuffDefinition:
        return BUFF_DEFINITIONS[self.type]


BUFF_DEFINITIONS = {
    BuffType.APPLE_MAGNET: BuffDefinition(
        type=BuffType.APPLE_MAGNET,
        friendly_name="Apple Magnet",
        default_duration=8,
        is_debuff=False,
        application_frequency=BuffApplicationFrequency.REPEATING,
        application_time=BuffApplicationTime.POST_STEP,
        applies_globally=False,
    ),
    BuffType.APPLE_REPEL: BuffDefinition(
        type=BuffType.APPLE_REPEL,
        friendly_name="Apple Repellent",
        default_duration=4,
        is_debuff=True,
        application_frequency=BuffApplicationFrequency.REPEATING,
        application_time=BuffApplicationTime.POST_STEP,
        applies_globally=False,
    ),
    BuffType.TICK_PERIOD_BOOST: BuffDefinition(
        type=BuffType.TICK_PERIOD_BOOST,
        friendly_name="Speed Boost",
        default_duration=12,
        is_debuff=False,
        application_frequency=BuffApplicationFrequency.ONCE,
        application_time=BuffApplicationTime.POST_STEP,
        applies_globally=True,
    ),
    BuffType.GHOST: BuffDefinition(
        type=BuffType.GHOST,
        friendly_name="Ghost",
        default_duration=8,
        is_debuff=False,
        application_frequency=BuffApplicationFrequency.ONCE,
        application_time=BuffApplicationTime.POST_STEP,
        applies_globally=False,
    ),
}
